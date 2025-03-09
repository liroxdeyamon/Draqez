from enum import Enum, auto

class Modes(Enum):
    MODE_MENU = auto()
    MODE_PLAY = auto()

class WeaponTypes(Enum):
    INSTANT_SHOOT = auto()
    CHARGING_SHOOT = auto()

    MANUAL_RELOADING_AMMO = auto()
    AUTO_RELOADING_AMMO = auto()
    ON_KILL_AMMO = auto()
    DAMAGE_TAKEN_AMMO = auto()


class Teams(Enum):
    TEAM_PLAYER = auto()
    TEAM_ENEMY = auto()
    TEAM_3 = auto()
    TEAM_4 = auto()
    TEAM_5 = auto()
    TEAM_6 = auto()
    TEAM_7 = auto()
    TEAM_8 = auto()
    TEAM_9 = auto()
    TEAM_10 = auto()
    TEAM_11 = auto()
    TEAM_12 = auto()
    TEAM_13 = auto()
    TEAM_14 = auto()
    TEAM_15 = auto()
    TEAM_16 = auto()
    TEAM_17 = auto()

TEAM_COLORS = {
    Teams.TEAM_PLAYER: (50,50,255),
    Teams.TEAM_ENEMY: (255,0,0)
}