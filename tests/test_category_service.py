from tests.test_base import BaseTest
from models import Category

class TestCategoryService(BaseTest):
    """
    Pruebas unitarias para la clase CategoryService.
    """
    def test_create_category_success(self):
        """
        Verifica que se puede crear una categoría con éxito.
        """
        category_data = {"nombre": "Test Category"}
        category = self.category_service.create_category(category_data)
        self.assertIsInstance(category, Category)
        self.assertEqual(category.nombre, "Test Category")
        self.assertIsNotNone(category.id_categoria)

    def test_create_category_missing_name(self):
        """
        Verifica que la creación de categoría falla si falta el nombre.
        """
        with self.assertRaises(ValueError) as cm:
            self.category_service.create_category({})
        self.assertIn("El nombre de la categoría es obligatorio y debe ser una cadena no vacía.", str(cm.exception))

    def test_create_category_duplicate_name(self):
        """
        Verifica que la creación de categoría falla con un nombre duplicado.
        """
        self.category_service.create_category({"nombre": "Unique Category"})
        with self.assertRaises(ValueError) as cm:
            self.category_service.create_category({"nombre": "Unique Category"})
        self.assertIn("Ya existe una categoría con el nombre: Unique Category", str(cm.exception))

    def test_get_category_by_id_success(self):
        """
        Verifica que se puede obtener una categoría por su ID.
        """
        category = self.category_service.create_category({"nombre": "Fetch Category"})
        fetched_category = self.category_service.get_category_by_id(category.id_categoria)
        self.assertIsNotNone(fetched_category)
        self.assertEqual(fetched_category.id_categoria, category.id_categoria)

    def test_get_category_by_id_not_found(self):
        """
        Verifica que se devuelve None si la categoría no se encuentra.
        """
        fetched_category = self.category_service.get_category_by_id(999)
        self.assertIsNone(fetched_category)

    def test_get_category_by_id_invalid_id(self):
        """
        Verifica que la obtención de categoría falla con un ID inválido.
        """
        with self.assertRaises(ValueError) as cm:
            self.category_service.get_category_by_id(0)
        self.assertIn("El ID de categoría debe ser un entero positivo.", str(cm.exception))

    def test_get_all_categories_success(self):
        """
        Verifica que se pueden obtener todas las categorías.
        """
        self.category_service.create_category({"nombre": "Category A"})
        self.category_service.create_category({"nombre": "Category B"})
        categories = self.category_service.get_all_categories()
        self.assertEqual(len(categories), 2)

    def test_update_category_success(self):
        """
        Verifica que se puede actualizar una categoría con éxito.
        """
        category = self.category_service.create_category({"nombre": "Update Category"})
        updated_category = self.category_service.update_category(category.id_categoria, {"nombre": "Updated Category Name"})
        self.assertIsNotNone(updated_category)
        self.assertEqual(updated_category.nombre, "Updated Category Name")

    def test_update_category_not_found(self):
        """
        Verifica que la actualización de categoría devuelve None si no se encuentra.
        """
        updated_category = self.category_service.update_category(999, {"nombre": "Non Existent Category"})
        self.assertIsNone(updated_category)

    def test_update_category_invalid_data(self):
        """
        Verifica que la actualización de categoría falla con datos inválidos.
        """
        category = self.category_service.create_category({"nombre": "Valid Category"})
        with self.assertRaises(ValueError) as cm:
            self.category_service.update_category(category.id_categoria, {"nombre": ""})
        self.assertIn("El nombre de la categoría debe ser una cadena no vacía.", str(cm.exception))

    def test_delete_category_success(self):
        """
        Verifica que se puede eliminar una categoría con éxito.
        """
        category = self.category_service.create_category({"nombre": "Delete Category"})
        deleted = self.category_service.delete_category(category.id_categoria)
        self.assertTrue(deleted)
        self.assertIsNone(self.category_service.get_category_by_id(category.id_categoria))

    def test_delete_category_not_found(self):
        """
        Verifica que la eliminación de categoría devuelve False si no se encuentra.
        """
        deleted = self.category_service.delete_category(999)
        self.assertFalse(deleted)

    def test_delete_category_invalid_id(self):
        """
        Verifica que la eliminación de categoría falla con un ID inválido.
        """
        with self.assertRaises(ValueError) as cm:
            self.category_service.delete_category(-1)
        self.assertIn("El ID de categoría debe ser un entero positivo.", str(cm.exception))
