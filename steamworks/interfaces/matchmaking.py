from ctypes import *
from enum import Enum

import steamworks.util as util
from steamworks.enums import *
from steamworks.structs import *
from steamworks.exceptions import *


class SteamMatchmaking(object):
    # Callback function types (Match SDK)
    _LobbyCreated_t = CFUNCTYPE(None, LobbyCreated_t)
    _LobbyEnter_t = CFUNCTYPE(None, LobbyEnter_t)
    _GameLobbyJoinRequested_t = CFUNCTYPE(None, GameLobbyJoinRequested_t)

    # Instance variables to store callback functions
    _LobbyCreated = None
    _LobbyEnter = None
    _GameLobbyJoinRequested = None

    def _create_lobby_callback(self, result):
        print("Lobby created callback")
        if result.m_eResult == EResult.OK.value:
            self.current_lobby_id = result.m_ulSteamIDLobby
            print("Lobby created: ", self.current_lobby_id)
            self._refresh_lobby_members()

    def _lobby_enter_callback(self, result):
        print("Lobby enter callback")
        # print all attributes of result
        if (False):
            for attr in dir(result):
                print("obj.%s = %r" % (attr, getattr(result, attr)))
        print("Status", result.m_EChatRoomEnterResponse)
        if result.m_EChatRoomEnterResponse == 1:
            self.current_lobby_id = result.m_ulSteamIDLobby
            self._refresh_lobby_members()
            print("Joined lobby: ", self.current_lobby_id)
            print("Lobby members: ", self.lobby_members)

    def __init__(self, steam: object):
        self.steam = steam
        if not self.steam.loaded():
            raise SteamNotLoadedException("STEAMWORKS not yet loaded")

        # --- State ---
        self.current_lobby_id = 0
        self.lobby_members = []  # List of member Steam IDs (uint64)
        self.SetLobbyCreatedCallback(self._create_lobby_callback)
        self.SetLobbyEnterCallback(self._lobby_enter_callback)

    def SetLobbyCreatedCallback(self, callback: object) -> bool:
        self._LobbyCreated = SteamMatchmaking._LobbyCreated_t(callback)
        self.steam.Lobby_SetLobbyCreatedCallback(self._LobbyCreated)
        return True

    def SetLobbyEnterCallback(self, callback: object) -> bool:
        self._LobbyEnter = SteamMatchmaking._LobbyEnter_t(callback)
        self.steam.Lobby_SetLobbyEnterCallback(self._LobbyEnter)
        return True

    def SetGameLobbyJoinRequestedCallback(self, callback: object) -> bool:
        self._GameLobbyJoinRequested = self._GameLobbyJoinRequested_t(callback)
        self.steam.Lobby_SetGameLobbyJoinRequestedCallback(self._GameLobbyJoinRequested)
        return True

    def CreateLobby(self, lobby_type: ELobbyType, max_members: int) -> None:
        self.steam.CreateLobby(lobby_type.value, max_members)

    def JoinLobby(self, steam_lobby_id: int) -> None:
        self.steam.JoinLobby(steam_lobby_id)

    def LeaveLobby(self, steam_lobby_id: int) -> None:
        self.steam.LeaveLobby(steam_lobby_id)
        self.current_lobby_id = 0  # Reset lobby ID
        self.lobby_members = []  # Clear members

    def InviteUserToLobby(self, steam_lobby_id: int, steam_id_invitee: int) -> bool:
        return self.steam.InviteUserToLobby(steam_lobby_id, steam_id_invitee)

    def GetNumLobbyMembers(self) -> int:
        return self.steam.GetNumLobbyMembers(self.current_lobby_id)

    def GetLobbyMemberByIndex(self, steam_lobby_id: int, member_index: int) -> int:
        return self.steam.GetLobbyMemberByIndex(steam_lobby_id, member_index)

    def _refresh_lobby_members(self):
        """Internal helper to update the lobby_members list."""
        self.lobby_members = []  # Clear existing members
        if self.current_lobby_id != 0:
            num_members = self.GetNumLobbyMembers()
            for i in range(num_members):
                member_id = self.GetLobbyMemberByIndex(self.current_lobby_id, i)
                self.lobby_members.append(member_id)

    def GetLobbyMembers(self) -> list:
        """
        Returns lobby members list
        :return: list
        """
        return self.lobby_members

    def GetCurrentLobbyId(self) -> int:
        return self.current_lobby_id
