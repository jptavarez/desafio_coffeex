from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from api.models import Stock

class StockTests(APITestCase):

    password = 'testing'

    def setUp(self):
        manager_user = User.objects.create_user(
            username='testusermanager', 
            email='testuser@test.com', 
            password=self.password
        )
        manager_user.profile.coffeex_manager = True 
        manager_user.save()
        self.manager_user = manager_user
    
        normal_user = User.objects.create_user(
            username='testusernormal', 
            email='testusernormal@test.com', 
            password=self.password
        )
        self.normal_user = normal_user   
    
    def test_create_stock(self):
        self._normal_user_login()
        name = 'Teste Estoque Normal User'
        capacity = 500
        response = self._create_stock(name, capacity)
        data = response.data
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Stock.objects.count(), 1)
        self.assertEqual(data['available_bags'], 0)
        self.assertEqual(data['withdrawal_quantity'], 0)
        self.assertEqual(data['coffee_types'], [])
        self.assertEqual(data['origin_farms'], [])
        self.assertEqual(data['owner'], self.normal_user.id)
        self.assertEqual(data['name'], name)
        self.assertEqual(data['capacity'], capacity)
        self.client.logout()  
    
    def test_stock_access_permission(self):
        # creating stock for the manager_user that will be used in the test
        self._manager_user_login()
        response = self._create_stock(name='Teste Estoque Manager User', capacity=500)    
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Stock.objects.count(), 1)
        stock_manager_user = response.data['id']
        self.client.logout()

        # creating stock for the normal_user that will be used in the test
        self._normal_user_login()
        response = self._create_stock(name='Teste Estoque Normal User', capacity=500)   
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Stock.objects.count(), 2)
        stock_normal_user = response.data['id']

        # Normal users must be allowed to access only stocks that belong to them 
        response = self.client.get(reverse('stock-detail', kwargs={'pk':stock_manager_user}), format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND) # TODO: it should not be 404
        response = self.client.get(reverse('stock-detail', kwargs={'pk':stock_normal_user}), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.logout()

        # manager_user must be allowed to access all stocks
        self._manager_user_login()
        response = self.client.get(reverse('stock-detail', kwargs={'pk':stock_manager_user}), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(reverse('stock-detail', kwargs={'pk':stock_normal_user}), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data 
        self.assertEqual(data['name'], 'Teste Estoque Normal User')
        self.assertEqual(data['capacity'], 500)

    def test_list_stocks(self):
        """
            it must be listed only stocks that the user is allowed to access.
        """
        self._manager_user_login()
        response = self._create_stock(name='Teste Estoque Manager User', capacity=500)    
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Stock.objects.count(), 1)
        self.client.logout()

        self._normal_user_login()
        response = self._create_stock(name='Teste Estoque Normal User', capacity=500)    
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Stock.objects.count(), 2)
        self.client.logout()

        self._normal_user_login()
        response = self.client.get(reverse('stock-list'), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.client.logout()

        self._manager_user_login()
        response = self.client.get(reverse('stock-list'), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)        
        for data in response.data:
            self.assertIn('available_bags', data)
            self.assertIn('withdrawal_quantity', data)
            self.assertIn('coffee_types', data)
            self.assertIn('origin_farms', data)
            self.assertIn('owner', data)
            self.assertIn('name', data)
            self.assertIn('capacity', data)
        self.client.logout()
    
    def test_update_stock(self):
        self._normal_user_login()
        response = self._create_stock(name='Teste Estoque', capacity=500)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Stock.objects.count(), 1)
        stock_id = response.data['id']
        name = 'Teste Estoque Update'
        capacity = 400
        response = self._update_stock(stock_id, name, capacity)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        self.assertEqual(data['name'], name)
        self.assertEqual(data['capacity'], capacity)
        self.client.logout()
    
    def test_permission_update_stock(self):
        self._manager_user_login()
        response = self._create_stock(name='Teste Estoque', capacity=500)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Stock.objects.count(), 1)
        stock_id = response.data['id']
        name = 'teste'
        capacity = 60
        response = self._update_stock(stock_id, name, capacity)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        self.assertEqual(data['name'], name)
        self.assertEqual(data['capacity'], capacity)
        self.client.logout()

        # Normal user can not update a stock created by a manager uer
        self._normal_user_login()
        response = self._update_stock(stock_id, 'teste2', 70)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND) # TODO: it should not be 404
        self.client.logout()
    
    def test_crop(self):
        self._manager_user_login()
        
        # Creating Stock to be used in the test
        name = 'Teste Estoque Manage User'
        capacity = 500
        response = self._create_stock(name, capacity)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        stock_manager = response.data['id']

        # Creating coffee_type to be used in the test
        response = self._create_coffee_type('Teste Coffee Type')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        coffee_type = response.data['id']

        # Creating farm to be used in the test
        response = self._create_farm('Teste Farm')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        farm = response.data['id']

        # Inserting crop with quantity higher than the available space in stock
        shelf_life = '2021-01-01'
        response = self._create_crop(
            stock=stock_manager, 
            coffee_type=coffee_type, 
            farm=farm, 
            shelf_life=shelf_life,
            quantity=600 # more than stock capacity
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['quantity'], 'Espaço insuficiente no estoque. Espaço disponível: 500')
        
        # Inserting a crop
        response = self._create_crop(
            stock=stock_manager, 
            coffee_type=coffee_type, 
            farm=farm, 
            shelf_life=shelf_life,
            quantity=100 
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.data
        crop_manager = data['id']
        self.assertEqual(data['stock'], stock_manager)
        self.assertEqual(data['coffee_type'], coffee_type)
        self.assertEqual(data['farm'], farm)
        self.assertEqual(data['shelf_life'], shelf_life)
        self.assertEqual(data['quantity'], 100)
        self.assertEqual(data['withdrawal_quantity'], 0)
        self.assertEqual(data['available_bags'], 100)

        # Withdrawing more bags than available 
        response = self._withdrawal(crop_manager, 200)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['quantity'], 'Quantidade de sacas não disponível. Quantidade disponível: 100')

        # Withdrawing correctly 
        response = self._withdrawal(crop_manager, 10)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        self.assertEqual(data['stock'], stock_manager)
        self.assertEqual(data['coffee_type'], coffee_type)
        self.assertEqual(data['farm'], farm)
        self.assertEqual(data['shelf_life'], shelf_life)
        self.assertEqual(data['quantity'], 100)
        self.assertEqual(data['withdrawal_quantity'], 10)
        self.assertEqual(data['available_bags'], 90)        
        self.client.logout() 

        # STARTING TESTS WITH THE NORMAL USER
        self._normal_user_login()

        # Normal users should not be allowed to withdrawal bags that don't belong to them        
        response = self._withdrawal(crop_manager, 10)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND) # TODO: it should not be 404
        
        # creating a stock for the normal user
        name = 'Teste Estoque normal User'
        capacity = 500
        response = self._create_stock(name, capacity)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        stock_normal_user = response.data['id']

        # It should not be possible for normal users to deposit crops into stocks that
        # don't belong to them.
        response = self._create_crop(
            stock=stock_manager, 
            coffee_type=coffee_type, 
            farm=farm, 
            shelf_life=shelf_life,
            quantity=100 
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['stock'], 'O usuário não possuí permissão para utilizar esse estoque.')

        # Correctly inserting a crop for the normal user
        response = self._create_crop(
            stock=stock_normal_user, 
            coffee_type=coffee_type, 
            farm=farm, 
            shelf_life=shelf_life,
            quantity=100 
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        crop_normal_user = response.data['id']

        # Normal users must be allowed to access only crops that belong to them 
        response = self.client.get(reverse('crop-detail', kwargs={'pk':crop_manager}), format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND) # TODO: it should not be 404
        response = self.client.get(reverse('crop-detail', kwargs={'pk':crop_normal_user}), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # it must return only crops that belong to the normal user
        response = self.client.get(reverse('crop-list'), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)        
        self.client.logout() 

        # USING THE MANAGER USER AGAIN
        self._manager_user_login()

        # Manager user should be allowed to access all crops        
        response = self.client.get(reverse('crop-list'), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        # The Stock has 90 bags available, so it should not be possible 
        # to update its capacity to an amount smaller then 90.
        response = self._update_stock(stock_manager, 'Teste update stock', 80)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)        
        self.assertEqual(response.data['capacity'], 'A capacidade do estoque não pode ser menor que a quantidade de sacas disponível no estoque.')

        # it should not be possible to delete stocks that have bags deposited
        response = self.client.delete(reverse('stock-detail', kwargs={'pk':stock_manager}), format='json') 
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST) 
        self.assertEqual(response.data['stock'], 'Não é possível deletar um estoque que possui sacas disponíveis.') 

    def _create_crop(self, stock, coffee_type, farm, shelf_life, quantity):
        dto = {
            'stock': stock,
            'coffee_type': coffee_type,
            'farm': farm,
            'shelf_life': shelf_life,
            'quantity': quantity
        }
        return self.client.post(reverse('crop-list'), dto, format='json')
    
    def _withdrawal(self, crop, quantity):
        dto = {
            'quantity': quantity
        }
        return self.client.put(reverse('crop-withdrawal', kwargs={'pk':crop}), dto, format='json')
            
    def _create_coffee_type(self, name):
        dto = {
            'name': name
        }
        return self.client.post(reverse('coffee-type-list'), dto, format='json')
    
    def _create_farm(self, name):
        dto = {
            'name': name
        }
        return self.client.post(reverse('farm-list'), dto, format='json')
    
    def _create_stock(self, name, capacity):
        dto = {
            'name': name,
            'capacity': capacity
        }
        return self.client.post(reverse('stock-list'), dto, format='json')
    
    def _update_stock(self, stock_id, name, capacity):
        dto = {
            'name': name,
            'capacity': capacity
        }
        return self.client.put(reverse('stock-detail', kwargs={'pk':stock_id}), dto, format='json')
    
    def _delete_stock(self, stock_id, name, capacity):
        dto = {
            'name': name,
            'capacity': capacity
        }
        return self.client.put(reverse('stock-detail', kwargs={'pk':stock_id}), dto, format='json')
    
    def _manager_user_login(self):
        self.client.login(username=self.manager_user.username, password=self.password)
    
    def _normal_user_login(self):
        self.client.login(username=self.normal_user.username, password=self.password)


         


        
        
        


