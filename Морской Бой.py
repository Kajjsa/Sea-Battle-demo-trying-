class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f'Dot({self.x}, {self.y})'


class BoardException(Exception):
    pass


class BoardOutException(BoardException):
    def __str__(self):
        return 'Выстрел за пределами границ поля!'


class BoardUsedException(BoardException):
    def __str__(self):
        return 'В клетку уже стреляли!'


class BoardWrongShipException(BoardException):
    pass


class Ship:
    def __init__(self, bow, d, o):
        self.bow = bow
        self.d = d
        self.o = o
        self.decks = d

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.d):
            line_x = self.bow.x
            line_y = self.bow.y

            if self.o == 0:
                line_x += i
            elif self.o == 1:
                line_y += i

            ship_dots.append(Dot(line_x, line_y))

        return ship_dots

    def casualty(self, shot):
        return shot in self.dots


class Board:
    def __init__(self, hide=False, size=6):
        self.size = size
        self.hide = hide

        self.count = 0

        self.field = [['O']*size for _ in range(size)]

        self.occupied = []
        self.ships = []

    def __str__(self):
        border = ''
        border += '|1|2|3|4|5|6'
        for i, row in enumerate(self.field):
            border += f'\n{i+1}|"+"| ".join(row)+"|'

        if self.hide:
            border = border.replace('*', 'O')
        return border

    def out(self, d):
        return not((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def frame(self, ship, issue=False):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, 1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                line = Dot(d.x + dx, d.y + dy)
                if not(self.out(line)) and line not in self.occupied:
                    if issue:
                        self.field[line.x][line.y] = '.'
                    self.occupied.append(line)

    def add_ship(self, ship):
        for d in ship.dots:
            if self.out(d) or d in self.occupied:
                raise BoardWrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = '*'
            self.occupied.append(d)

        self.ships.append(ship)
        self.frame(ship)

    def shot(self, d):
        if self.out(d):
            raise BoardOutException()

        if d in self.occupied:
            raise BoardUsedException()

        self.occupied.append(d)

        for ship in self.ships:
            if ship.casualty(d):
                ship.decks -= 1
                self.field[d.x][d.y] = 'X'
                if ship.decks == 0:
                    self.count += 1
                    self.frame(ship, issue=True)
                    print('Убит!')
                    return False
                else:
                    print('Ранен!')
                    return True

        self.field[d.x][d.y] = '.'
        print('Мимо!')
        return False

    def begin(self):
        self.occupied = []

    def defeat(self):
        return self.count == len(self.ships)


class Player:
    def __init__(self, area, rival):
        self.area = area
        self.rival = rival

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.rival.shot(target)
                return repeat
            except BoardException as e:
                print(e)


class PC(Player):
    def __init__(self, area, rival):
        super().__init__(area, rival)
        self.board = None

    def ask(self):
        d = Dot((0, 5), (0, 5))
        print(f'Ход Компьютера: {d.x + 1} {d.y + 1}')
        return d


class User(Player):
    def __init__(self, area, rival):
        super().__init__(area, rival)
        self.board = None

    def ask(self):
        while True:
            point = input('Ваш Ход:').split()

            if len(point) != 2:
                print('Введите 2 кооридинаты!')
                continue

            x, y = point

            if not(x.isdigit()) or not(y.isdigit()):
                print('Введите число!')
                continue

            x, y = int(x), int(y)

            return Dot(x-1, y-1)


class Game:
    def __init__(self, size=6):
        self.length = [3, 2, 2, 1, 1, 1, 1]
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hide = True

        self.pc = PC(co, pl)
        self.us = User(pl, co)

    def try_board(self):
        board = Board(size=self.size)
        attempt = 0
        for l in self.length:
            while True:
                attempt += 1
                if attempt > 2000:
                    return None
                ship = Ship(Dot(0, self.size), l, (0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def random_board(self):
        board = None
        while board is None:
            board = self.try_board()
        return board

    def welcome(self):
        print('-----------')
        print('Морской Бой')
        print('-----------')
        print('')
        print('Правила ввода координат:')
        print('------------------------')
        print('* 1-ая координата - строка.')
        print('* 2-ая координата - столбец.')
        print('* Между координатами ставится пробел.')
        print(' ')

    def rules(self):
        num = 0
        while True:
            print('-'*20)
            print('Поле Игрока:')
            print(self.us.board)
            print('-'*20)
            print('Поле Компьютера:')
            print(self.pc.board)
            print('-'*20)
            if num % 2 == 0:
                print('Ход Игрока')
                repeat = self.us.move()
            else:
                print('Ход Компьютера')
                repeat = self.pc.move()
            if repeat:
                num -= 1
            if self.pc.board.defeat():
                print('-'*20)
                print('Победа Игрока!')
                break
            if self.us.board.defeat():
                print('-'*20)
                print('Победа Компьютера!')
                break
            num += 1

    def start(self):
        self.welcome()
        self.rules()


g = Game()
g.start()
