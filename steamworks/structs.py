from ctypes import *


class FindLeaderboardResult_t(Structure):
    """Represents the STEAMWORKS LeaderboardFindResult_t call result type"""

    _fields_ = [("leaderboardHandle", c_uint64), ("leaderboardFound", c_uint32)]


class CreateItemResult_t(Structure):
    _fields_ = [
        ("result", c_int),
        ("publishedFileId", c_uint64),
        ("userNeedsToAcceptWorkshopLegalAgreement", c_bool),
    ]


class SubmitItemUpdateResult_t(Structure):
    _fields_ = [
        ("result", c_int),
        ("userNeedsToAcceptWorkshopLegalAgreement", c_bool),
        ("publishedFileId", c_uint64),
    ]


class ItemInstalled_t(Structure):
    _fields_ = [("appId", c_uint32), ("publishedFileId", c_uint64)]


class SubscriptionResult(Structure):
    _fields_ = [("result", c_int32), ("publishedFileId", c_uint64)]


class MicroTxnAuthorizationResponse_t(Structure):
    _fields_ = [("appId", c_uint32), ("orderId", c_uint64), ("authorized", c_bool)]


class LobbyCreated_t(Structure):
    _fields_ = [
        ("m_eResult", c_int),  # EResult enum (int) - Result of the lobby creation
        (
            "m_ulSteamIDLobby",
            c_uint64,
        ),  # CSteamID (uint64) - SteamID of the created lobby
    ]


class LobbyEnter_t(Structure):
    _fields_ = [
        ("m_ulSteamIDLobby", c_uint64),  # CSteamID (uint64) - SteamID of the lobby
        (
            "m_EChatRoomEnterResponse",
            c_int,
        ),  # EChatRoomEnterResponse enum (int) - Result of the lobby enter attempt
        (
            "m_rgfChatPermissions",
            c_int,
        ),  # int32 - Chat permissions in the lobby (flags)
        ("m_bLocked", c_bool),  # bool - True if the lobby is locked
        ("m_ulGameID", c_uint32),  # GameID_t (uint32) - GameID of the lobby
    ]


class GameLobbyJoinRequested_t(Structure):
    _fields_ = [
        (
            "m_steamIDLobby",
            c_uint64,
        ),  # CSteamID (uint64) - SteamID of the lobby being joined
        (
            "m_steamIDFriend",
            c_uint64,
        ),  # CSteamID (uint64) - SteamID of the friend who invited/requested join
    ]
