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

    def __init__(self, steam: object):
        self.steam = steam
        if not self.steam.loaded():
            raise SteamNotLoadedException("STEAMWORKS not yet loaded")

        # --- State ---
        self.current_lobby_id = 0
        self.lobby_members = []  # List of member Steam IDs (uint64)

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

    def CreateLobby(
        self, lobby_type: ELobbyType, max_members: int, callback: object = None
    ) -> None:
        if callback:
            self.SetLobbyCreatedCallback(callback)

        # Internal callback handler
        def on_lobby_created_internal(lobby_created):
            print("Lobby created callback")
            if lobby_created.result == EResult.OK:
                self.current_lobby_id = lobby_created.steam_id_lobby
                self._refresh_lobby_members()  # Get initial member list
            if self._LobbyCreated:  # Call the external callback
                self._LobbyCreated(lobby_created)

        # Register the internal callback
        self.SetLobbyCreatedCallback(on_lobby_created_internal)
        self.steam.CreateLobby(lobby_type.value, max_members)

    def JoinLobby(self, steam_lobby_id: int, callback: object = None) -> None:
        if callback:
            self.SetLobbyEnterCallback(callback)

        # Internal callback handler
        def on_lobby_enter_internal(lobby_enter):
            print("Lobby enter callback")
            if (
                lobby_enter.chat_room_enter_response == 1
            ):  # k_EChatRoomEnterResponseSuccess
                self.current_lobby_id = lobby_enter.steam_id_lobby
                self._refresh_lobby_members()  # Get member list
            if self._LobbyEnter:  # Call the external callback
                self._LobbyEnter(lobby_enter)

        # Register the internal callback
        self.SetLobbyEnterCallback(on_lobby_enter_internal)
        self.steam.JoinLobby(steam_lobby_id)

    def LeaveLobby(self, steam_lobby_id: int) -> None:
        self.steam.LeaveLobby(steam_lobby_id)
        self.current_lobby_id = 0  # Reset lobby ID
        self.lobby_members = []  # Clear members

    def InviteUserToLobby(self, steam_lobby_id: int, steam_id_invitee: int) -> bool:
        return self.steam.InviteUserToLobby(steam_lobby_id, steam_id_invitee)

    def GetNumLobbyMembers(self, steam_lobby_id: int) -> int:
        return self.steam.GetNumLobbyMembers(steam_lobby_id)

    def GetLobbyMemberByIndex(self, steam_lobby_id: int, member_index: int) -> int:
        return self.steam.GetLobbyMemberByIndex(steam_lobby_id, member_index)

    def _refresh_lobby_members(self):
        """Internal helper to update the lobby_members list."""
        self.lobby_members = []  # Clear existing members
        if self.current_lobby_id != 0:
            num_members = self.GetNumLobbyMembers(self.current_lobby_id)
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
