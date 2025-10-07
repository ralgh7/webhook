import os
import discord
from discord import app_commands
from dotenv import load_dotenv
from keyauth import api

# --- Configuration ---
# Load environment variables from a .env file for security
load_dotenv()

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
KEYAUTH_OWNER_ID = os.getenv("KEYAUTH_OWNER_ID")
KEYAUTH_APP_NAME = os.getenv("KEYAUTH_APP_NAME")
DISCORD_ROLE_ID = int(os.getenv("DISCORD_ROLE_ID")) # Make sure this is an integer

# --- Basic Validation ---
# Check if all required environment variables are set before starting
if not all([DISCORD_BOT_TOKEN, KEYAUTH_OWNER_ID, KEYAUTH_APP_NAME, DISCORD_ROLE_ID]):
    print("Error: One or more required environment variables are missing.")
    print("Please check your .env file and ensure all variables are set.")
    exit()

# --- KeyAuth API Initialization ---
try:
    keyauthapp = api(
        name=KEYAUTH_APP_NAME,
        ownerid=KEYAUTH_OWNER_ID,
        # The secret is not needed for license-only operations
        secret="", 
        version="1.0" # Version can be static for this purpose
    )
except Exception as e:
    print(f"Failed to initialize KeyAuth API: {e}")
    exit()

# --- Discord Bot Setup ---
# Define the necessary bot permissions (intents)
intents = discord.Intents.default()
intents.members = True # Required to manage roles

# Create the bot client instance
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

@client.event
async def on_ready():
    """Event handler for when the bot successfully connects to Discord."""
    await tree.sync() # Sync slash commands with Discord
    print(f"Logged in as {client.user} (ID: {client.user.id})")
    print("KeyAuth Bot is ready and listening for commands.")
    print("------")

# --- Bot Commands ---

@tree.command(name="activate", description="Activate your license key to get your role.")
@app_commands.describe(key="Your KeyAuth license key")
async def activate_key(interaction: discord.Interaction, key: str):
    """
    Handles the /activate command.
    Validates a KeyAuth key and assigns a role upon success.
    """
    # Defer the response to give the bot time to process the API call
    await interaction.response.defer(ephemeral=True)

    # Fetch the key data from KeyAuth API
    key_info = keyauthapp.license(key)

    # Check if the key validation was successful
    if key_info and key_info.get("success"):
        # Key is valid, now get the role from the server
        guild = interaction.guild
        role_to_assign = guild.get_role(DISCORD_ROLE_ID)

        if not role_to_assign:
            await interaction.followup.send("Error: The configured role could not be found on this server. Please contact an admin.")
            return

        try:
            # Add the role to the user
            await interaction.user.add_roles(role_to_assign)

            # IMPORTANT: Store the user's Discord ID in a KeyAuth user variable
            # This links their Discord account to their key for the /reset_hwid command
            keyauthapp.setvar(key_info["info"]["username"], "discordid", str(interaction.user.id))

            await interaction.followup.send(f"✅ Success! Your key has been activated and you've been given the `{role_to_assign.name}` role.")
        except discord.errors.Forbidden:
            await interaction.followup.send("Error: I don't have permission to assign roles. Make sure my role is higher than the one I'm trying to assign.")
        except Exception as e:
            await interaction.followup.send(f"An unexpected error occurred: {e}")
    else:
        # Key is invalid, send the error message from KeyAuth
        error_message = key_info.get("message", "Unknown error") if key_info else "Failed to connect to KeyAuth API."
        await interaction.followup.send(f"❌ Activation failed: `{error_message}`")


@tree.command(name="reset_hwid", description="Reset the Hardware ID (HWID) linked to your key.")
async def reset_hwid(interaction: discord.Interaction):
    """
    Handles the /reset_hwid command.
    Resets the HWID for the user's key if they have an active license.
    """
    await interaction.response.defer(ephemeral=True)
    
    # Check if the user has the required role
    role = interaction.guild.get_role(DISCORD_ROLE_ID)
    if role not in interaction.user.roles:
        await interaction.followup.send("You must activate a key first using `/activate` before you can reset your HWID.")
        return

    # Fetch user data from KeyAuth API using their Discord ID as the identifier
    # This requires the user's username, which we don't know directly.
    # So we must fetch the key from a user variable first.
    # NOTE: This part requires custom API logic or a seller panel action,
    # as the standard `api` class doesn't have a direct "get key by user variable" function.
    # For this example, we'll assume the username IS the key for simplicity,
    # or that a more direct method is available.
    
    # A more robust solution would be to use KeyAuth's seller API to fetch user info by a variable.
    # Since that's complex, we'll use a placeholder for the logic.
    # The `license()` function is often used to get user info if the key is known.
    
    # This is a conceptual implementation. You would typically need a way to
    # find the user's key via their Discord ID. A seller API call is best.
    # For now, we will inform the user of the action and simulate the call.
    
    # Let's try to get the user's KeyAuth username via another variable if you store it
    # For this example, we'll just demonstrate the HWID reset action directly
    # assuming we found their username.
    
    # We will use the user's discord name as a placeholder for their KeyAuth username
    # You should refine this logic based on how you store user data.
    keyauth_username = interaction.user.name 
    
    # A better way is to query all users and find the one with the matching discordid variable.
    # The public API client might not support this.
    # Let's show the direct HWID reset call assuming you have the user's key/username.
    # This is a limitation of the standard client library.
    
    # A practical workaround is to ask the user for their key again.
    # For now, let's just make a placeholder error.
    
    # To make this fully functional, you would need to either:
    # 1. Use the KeyAuth Seller API to search users by the `discordid` variable.
    # 2. Ask the user for their key again in this command.
    
    # Let's go with option 2 for a working example.
    await interaction.followup.send("To reset your HWID, please use the `/reset_hwid_with_key` command and provide your key.")

@tree.command(name="reset_hwid_with_key", description="Reset HWID using your license key.")
@app_commands.describe(key="Your KeyAuth license key to reset the HWID for")
async def reset_hwid_with_key(interaction: discord.Interaction, key: str):
    """ A more practical HWID reset command that uses the key for lookup. """
    await interaction.response.defer(ephemeral=True)

    # Validate the key first
    key_info = keyauthapp.license(key)
    if not (key_info and key_info.get("success")):
        await interaction.followup.send("❌ The provided key is not valid.")
        return
        
    # Get the user info from the key data
    user_info = key_info.get("info", {})
    keyauth_username = user_info.get("username")

    if not keyauth_username:
        await interaction.followup.send("Could not retrieve user information from this key.")
        return

    # Reset the HWID
    reset_response = keyauthapp.hwid(keyauth_username) # HWID reset usually requires username

    if reset_response and reset_response.get("success"):
        await interaction.followup.send("✅ Your HWID has been successfully reset.")
    else:
        error_message = reset_response.get("message", "Unknown error")
        await interaction.followup.send(f"❌ Failed to reset HWID: `{error_message}`")


# --- Start the Bot ---
if __name__ == "__main__":
    client.run(DISCORD_BOT_TOKEN)
