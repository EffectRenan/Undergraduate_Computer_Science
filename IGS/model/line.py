from model.object import Object
from math import isclose
from random import randint

def close_to_zero(num: float) -> bool:
#Centralzie comparisons with zero for this module
        return isclose(num, 0, abs_tol=1e-6)

class Line(Object):

    def __init__(self) -> None:
        super().__init__("Line")
        self._mtl_prefix = "l"

    def _check(self, coordinates: list) -> list:
        if coordinates != None:
            if len(coordinates) != 2 or \
                not isinstance(coordinates[0], tuple):

                raise Exception("Line error: The format must be (x0, y0),(x1, y1).")

        return coordinates

    def _parsing(self, string_coordinates: str) -> list:
        return list(self._string_to_tuple(string_coordinates))

    def clipping(self, window: list) -> None:
        # window:
        # [0]: (xMim, xMax)
        # [1]: (ymin, yMax)

        # Coordenadas: self.coordinates

        # Salva as coordenadas resultantes em self.coordinates
        # Caso tiver completamente fora da window, faça self.coordinates = None

        if randint(0, 1) == 0:
            self.__cohen_sutherland(window)
        else:
            self.LiangBarsky(window)

    def LiangBarsky(self, window: list):

        p1 =  self.coordinates[0]
        p2 =  self.coordinates[1]

        #Initialize values for equations
        pq_list = [
            {
                'p': -(p2[0] -  p1[0]),
                'q':  p1[0] - window[0][0]
            },
            {
                'p': ( p2[0] -  p1[0]),
                'q': window[0][1] -  p1[0]
            },
            {
                'p': -( p2[1] -  p1[1]),
                'q':  p1[1] - window[1][0]
            },
            {
                'p': ( p2[1] -  p1[1]),
                'q': window[1][1] -  p1[1]
            }
        ]

        self.is_inside = not any([close_to_zero(k['p'])
                                  and k['q'] < 0
                                  for k in pq_list])

        #get_clipped

        if not self.is_inside: 
            self.coordinates = None
            
        positives = [d for d in pq_list if not close_to_zero(
            d['p']) and d['p'] > 0]
        negatives = [d for d in pq_list if not close_to_zero(
            d['p']) and d['p'] < 0]

        positives = [d['q']/d['p'] for d in positives]
        negatives = [d['q']/d['p'] for d in negatives]

        u1 = max([0] + negatives)
        u2 = min([1] + positives)

        if u1 > u2:
            self.coordinates = None
            

        #(x0, y0),(x1, y1)
        new_line =[ ( p1[0] + pq_list[1]['p'] * u1,  p1[1] +pq_list[3]['p'] * u1 ),
        (  p1[0] + pq_list[1]['p'] * u2 , p1[1] + pq_list[3]['p'] * u2 ) ]

        if new_line is None:
            self.coordinates =  None
        else:
            self.coordinates = new_line
        
        pass

    def __cohen_sutherland(self, window: list) -> None:
        # window:
        # [0]: (xMim, xMax)
        # [1]: (ymin, yMax)

        # bits: 1 2 3 4
        # 1 top 
        # 2 bottom
        # 3 right 
        # 4 left 

        p1 = self.coordinates[0]
        p2 = self.coordinates[1]

        p1_rc = self.__region_code(p1, window)
        p2_rc = self.__region_code(p2, window)
        
        m = self.__slope(p1, p2);

        if int(p1_rc, 2) | int(p2_rc, 2) == 0: # All in 
            pass
        elif p1_rc == p2_rc: # All out
            self.coordinates = None
        else:
            if p1_rc != self.__correct_bin(0):
                p1 = self.__partial(p1, p1_rc, window, m)
            if p2_rc != self.__correct_bin(0):
                p2 = self.__partial(p2, p2_rc, window, m)

            if p1 == None or p2 == None:
                self.coordinates = None
            else:
                self.coordinates = [p1, p2]
            
    def __partial(self, p: tuple, p_rc: bin, window: list, m: float) -> tuple:
        x = None
        y = None
        
        if p_rc[0] == '1': # Top
            y = window[1][1] # yMax
            x = p[0] + (1 / m) * (y - p[1])
            if x >= window[0][0] and x <= window[0][1]:
                return (x, y)
        if p_rc[1] == '1': # bottom
            y = window[1][0] # yMin
            x = p[0] + (1 / m) * (y - p[1])
            if x >= window[0][0] and x <= window[0][1]:
                return (x, y)
        if p_rc[2] == '1': # right
            x = window[0][1] # xMax
            y = m * (x - p[0]) + p[1]
            if y >= window[1][0] and y <= window[1][1]:
                return (x, y)
        if p_rc[3] == '1': # left
            x = window[0][0] # xMin
            y = m * (x - p[0]) + p[1]
            if y >= window[1][0] and y <= window[1][1]:
                return (x, y)

        return None

    def __slope(self, p1: float, p2: float) -> float:
        return (p2[1] - p1[1]) / (p2[0] - p1[0])

    def __correct_bin(self, b: int) -> bin:
        fix_length = 4
        return bin(b)[2:].zfill(fix_length)

    def __region_code(self, p: tuple, window: list) -> bin:
        p_rc = None

        if p[0] < window[0][0]:        # x < xMin
            if p[1] < window[1][0]:    # y < yMin
                p_rc = self.__correct_bin(5)
            elif p[1] < window[1][1]:  # y < yMax
                p_rc = self.__correct_bin(1)
            else:
                p_rc = self.__correct_bin(9)
        elif p[0] < window[0][1]:
            if p[1] < window[1][0]:    # y < yMin
                p_rc = self.__correct_bin(4)
            elif p[1] < window[1][1]:  # y < yMax
                p_rc = self.__correct_bin(0)
            else:
                p_rc = self.__correct_bin(8)
        else:
            if p[1] < window[1][0]:    # y < yMin
                p_rc = self.__correct_bin(6)
            elif p[1] < window[1][1]:  # y < yMax
                p_rc = self.__correct_bin(2)
            else:
                p_rc = self.__correct_bin(10)

        return p_rc
