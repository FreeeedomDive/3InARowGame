from enum import Enum, unique, auto


@unique
class Types(Enum):
    Red = auto()
    Blue = auto()
    Yellow = auto()
    Green = auto()
    Purple = auto()
    Orange = auto()
    Grey = auto()


types = (Types.Red, Types.Blue, Types.Yellow, Types.Green,
         Types.Purple, Types.Orange, Types.Grey)

colors = ((200, 0, 0), (0, 0, 200), (230, 230, 0), (0, 160, 0), (204, 51, 255),
          (255, 150, 51), (140, 140, 140))

type_to_color = {Types.Red: colors[0],
                 Types.Blue: colors[1],
                 Types.Yellow: colors[2],
                 Types.Green: colors[3],
                 Types.Purple: colors[4],
                 Types.Orange: colors[5],
                 Types.Grey: colors[6]}

pics = ()
