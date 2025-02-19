from steamworks import STEAMWORKS, EP2PSend, ELobbyType
from ctypes import c_byte, c_int, c_ulonglong, c_uint, c_uint64, byref
import time


class SteamManager:
    def __init__(self):
        self.steamworks = STEAMWORKS()
        try:
            self.steamworks.initialize()
            print("SteamManager: Steam Initialized!")
            print(f"SteamManager: Player name: {self.steamworks.GetPersonaName()}")
            print(f"SteamManager: Player Steam ID: {self.steamworks.GetSteamID()}")
        except Exception as e:
            print(f"SteamManager: Error initializing Steam: {e}")
            self.steamworks = None  # Indicate Steam initialization failure

        self.friend_steam_id_to_invite = 0  # Set this externally
        self.friend_steam_id_p2p = 0  # Steam ID of friend in P2P session
        self.p2p_message_to_send = ""  # Set this before sending
        self.p2p_buffer_size = 1024
        self.p2p_buffer = (c_byte * self.p2p_buffer_size)()

    def is_steam_ready(self):
        return self.steamworks is not None and self.steamworks.loaded()

    def create_lobby(self, lobby_type=ELobbyType.k_ELobbyTypePublic, max_members=2):
        """Creates a lobby on Steam."""
        if not self.is_steam_ready():
            print("SteamManager: Steam not initialized, cannot create lobby.")
            return False

        print("SteamManager: Creating Lobby...")
        self.steamworks.Matchmaking.CreateLobby(lobby_type, max_members)
        print("SteamManager: Lobby creation requested.")
        return True  # Lobby creation requested, not yet confirmed. Handle callbacks for actual success.

    def join_lobby(self, lobby_id):
        """Joins an existing lobby."""
        if not self.is_steam_ready():
            print("SteamManager: Steam not initialized, cannot join lobby.")
            return False

        print(f"SteamManager: Joining Lobby: {lobby_id}...")
        self.steamworks.Matchmaking.JoinLobby(lobby_id)
        print("SteamManager: Join lobby requested.")
        return True  # Join lobby requested, not yet confirmed. Handle callbacks for actual success.

    def leave_lobby(self, lobby_id):
        """Leaves the current lobby."""
        if not self.is_steam_ready():
            print("SteamManager: Steam not initialized, cannot leave lobby.")
            return False

        print(f"SteamManager: Leaving Lobby: {lobby_id}...")
        self.steamworks.Matchmaking.LeaveLobby(lobby_id)
        print("SteamManager: Lobby leave requested.")
        return True

    def invite_friend_to_lobby(self, lobby_id, friend_steam_id):
        """Invites a friend to a lobby."""
        if not self.is_steam_ready():
            print("SteamManager: Steam not initialized, cannot invite friend.")
            return False

        print(lobby_id)
        if lobby_id == 0:
            print(
                "SteamManager: Error: No lobby ID available. Create or join a lobby first."
            )
            return False
        if friend_steam_id == 0:
            print("SteamManager: Error: friend_steam_id_to_invite is not set.")
            return False

        print(
            f"SteamManager: Inviting friend with SteamID: {friend_steam_id} to lobby {lobby_id}..."
        )
        success = self.steamworks.Matchmaking.InviteUserToLobby(
            lobby_id, friend_steam_id
        )
        if success:
            print("SteamManager: Invite sent successfully (may not be accepted yet).")
            return True
        else:
            print("SteamManager: Failed to send invite.")
            return False

    def send_p2p_message(self, remote_steam_id, message):
        """Sends a P2P message to a remote user."""
        if not self.is_steam_ready():
            print("SteamManager: Steam not initialized, cannot send P2P message.")
            return False

        if remote_steam_id == 0:
            print(
                "SteamManager: Error: remote_steam_id is not set. Ensure a P2P session is established and you know the recipient's Steam ID."
            )
            return False

        message_bytes = message.encode("utf-8")
        data_size = len(message_bytes)
        send_type = EP2PSend.k_EP2PSendReliableNoDelay.value

        print(f"SteamManager: Sending P2P message to {remote_steam_id}: '{message}'")
        success = self.steamworks.P2PNetworking.SendP2PPacket(
            remote_steam_id, message_bytes, data_size, send_type
        )
        if success:
            print("SteamManager: P2P message sent successfully.")
            return True
        else:
            print("SteamManager: Failed to send P2P message.")
            return False

    def receive_p2p_message(self):
        """Checks for and receives incoming P2P messages. Returns (message, sender_steam_id) or (None, None) if no message."""
        if not self.is_steam_ready():
            print("SteamManager: Steam not initialized, cannot receive P2P message.")
            return None, None

        msg_size = c_uint(0)  # Create a c_uint object to hold the message size
        sender_steam_id = c_uint64(
            0
        )  # Create a c_uint64 object to hold the sender SteamID

        received_data = self.steamworks.P2PNetworking.ReadP2PPacket(
            self.p2p_buffer,
            self.p2p_buffer_size,
            byref(msg_size),  # Pass a pointer to msg_size using byref()
            byref(sender_steam_id),  # Pass a pointer to sender_steam_id using byref()
        )

        if received_data:
            message_size_value = msg_size.value  # Get the value from the c_uint object
            sender_id_value = (
                sender_steam_id.value
            )  # Get the value from the c_uint64 object
            message = bytes(self.p2p_buffer)[:message_size_value]
            message = message.decode("utf-8")
            return message, sender_id_value
        else:
            return None, None

    def close_p2p_session(self, remote_steam_id):
        """Closes a P2P session with a remote user."""
        if not self.is_steam_ready():
            print("SteamManager: Steam not initialized, cannot close P2P session.")
            return False

        if remote_steam_id == 0:
            print("SteamManager: Error: remote_steam_id is not set.")
            return False

        print(f"SteamManager: Closing P2P session with {remote_steam_id}...")
        success = self.steamworks.P2PNetworking.CloseP2PSessionWithUser(remote_steam_id)
        if success:
            print("SteamManager: P2P session closed successfully.")
            return True
        else:
            print("SteamManager: Failed to close P2P session.")
            return False

    def create_p2p_session(self, remote_steam_id):
        """Creates a P2P session with a remote user."""
        if not self.is_steam_ready():
            print("SteamManager: Steam not initialized, cannot create P2P session.")
            return False

        if remote_steam_id == 0:
            print("SteamManager: Error: remote_steam_id is not set.")
            return False

        print(f"SteamManager: Creating P2P session with {remote_steam_id}...")
        success = self.steamworks.P2PNetworking.CreateP2PSessionWithUser(
            remote_steam_id
        )
        if success:
            print(
                "SteamManager: P2P session creation requested (success doesn't mean connection is established yet)."
            )
            return True  # Session creation requested, handle connection failures.
        else:
            print("SteamManager: Failed to request P2P session creation.")
            return False

    def run_callbacks(self):
        """Runs Steam callbacks. Call this frequently in your game loop."""
        if self.is_steam_ready():
            self.steamworks.run_callbacks()
        else:
            print("SteamManager: Steam not initialized, cannot run callbacks.")


if __name__ == "__main__":
    # Example usage of SteamManager for testing

    steam_manager = SteamManager()

    if not steam_manager.is_steam_ready():
        print("SteamManager Example: Steam initialization failed. Exiting.")
    else:
        print("SteamManager Example: Steam is ready.")

        # **IMPORTANT: SET YOUR FRIEND'S STEAM ID HERE FOR TESTING!**
        steam_manager.friend_steam_id_to_invite = (
            76561199229727717  # Replace with your friend's actual Steam ID64
        )
        steam_manager.friend_steam_id_p2p = steam_manager.friend_steam_id_to_invite

        steam_manager.create_p2p_session(steam_manager.friend_steam_id_p2p)

        while True:
            steam_manager.run_callbacks()  # Process Steam events

            print("\nSteamManager Example: Menu:")
            print("1. Create Lobby")
            print("2. Invite Friend to Lobby")
            print("3. Send P2P Message")
            print("4. Receive P2P Message")
            print("5. Leave Lobby")
            print("6. Join Lobby")
            print("7. Run callbacks")
            print("8. Check lobby")
            print("9. Overlay Test")
            print("10. Exit")

            choice = input("Enter your choice: ")

            if choice == "1":
                steam_manager.create_lobby()
                time.sleep(1)  # Give Steam some time to process
            elif choice == "2":
                lobby_id = steam_manager.steamworks.Matchmaking.GetCurrentLobbyId()
                steam_manager.invite_friend_to_lobby(
                    lobby_id, steam_manager.friend_steam_id_to_invite
                )
                time.sleep(1)
            elif choice == "3":
                steam_manager.p2p_message_to_send = input("Enter P2P message to send: ")
                steam_manager.send_p2p_message(
                    steam_manager.friend_steam_id_p2p, steam_manager.p2p_message_to_send
                )
                time.sleep(1)
            elif choice == "4":
                message, sender_id = steam_manager.receive_p2p_message()
                if message:
                    print(
                        f"SteamManager Example: Received message: '{message}' from {sender_id}"
                    )
                else:
                    print("SteamManager Example: No P2P message received.")
                time.sleep(1)
            elif choice == "5":
                steam_manager.leave_lobby(steam_manager.lobby_id)
                steam_manager.lobby_id = 0  # Reset local lobby id
                time.sleep(1)
            elif choice == "6":
                lobby_id = input("Enter the lobby ID to join: ")
                steam_manager.join_lobby(int(lobby_id))
                time.sleep(1)
            elif choice == "7":
                steam_manager.run_callbacks()
            elif choice == "8":
                lobby_id = steam_manager.steamworks.Matchmaking.GetCurrentLobbyId()
                print(f"SteamManager Example: Current lobby ID: {lobby_id}")
                num_players = steam_manager.steamworks.Matchmaking.GetNumLobbyMembers()
                print(
                    f"SteamManager Example: Number of players in lobby: {num_players}"
                )
                steam_manager.steamworks.Matchmaking._refresh_lobby_members()
                members = steam_manager.steamworks.Matchmaking.GetLobbyMembers()
                print(f"SteamManager Example: Lobby members: {members}")
            elif choice == "9":
                lobby_id = steam_manager.steamworks.Matchmaking.GetCurrentLobbyId()
                steam_manager.steamworks.Friends.ActivateGameOverlayInviteDialog(
                    lobby_id
                )
            elif choice == "10":
                print("SteamManager Example: Exiting.")
                break
            else:
                print("SteamManager Example: Invalid choice.")

            time.sleep(0.1)  # Small delay to prevent busy-waiting
