import unittest
import warnings
from cmr import queries


class TestIssue66(unittest.TestCase):
    def test_wkt_coordinate_order_warning(self):
        # 1. Usamos coordenadas que cruzan casi todo el mapa (Span > 180)
        # De 170 a -170 hay una diferencia de 340 grados.
        flipped_coords = [(170, 10), (-170, 10), (-170, -10), (170, -10), (170, 10)]

        query = queries.GranuleQuery()

        # 2. Ahora sí debería dispararse el UserWarning
        with self.assertWarns(UserWarning) as cm:
            query.polygon(flipped_coords)

        self.assertIn("longitude span is greater than 180 degrees", str(cm.warning))

    def test_bounding_box_order_warning(self):
        # Este ya pasaba, lo mantenemos igual
        query = queries.GranuleQuery()

        with self.assertWarns(UserWarning) as cm:
            query.bounding_box(10, 0, -10, 5)

        self.assertIn("crosses the antimeridian", str(cm.warning))


if __name__ == "__main__":
    unittest.main()
