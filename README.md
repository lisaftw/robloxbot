# Roblox Discord Bot

A powerful Discord bot designed specifically for Roblox community servers. This bot provides useful tools for server management, user verification, and Roblox-related information.

## Features

- **Roblox Profile Lookup**: Look up Roblox user profiles directly from Discord
- **Game Information**: Get details about Roblox games including player count and visits
- **User Verification**: Verify Discord users with their Roblox accounts
- **Role Management**: Automatically assign Discord roles based on Roblox groups and ranks
- **Embedded Messages**: All bot responses use embedded messages with a consistent Roblox-themed green color

## Commands

| Command | Description | Usage |
|---------|-------------|-------|
| `/profile <username>` | Look up a Roblox profile | `/profile Builderman` |
| `/game <game_id>` | Get information about a Roblox game | `/game 1818` |
| `/verify` | Start the verification process | `/verify` |
| `/roles` | Configure role management (Admin only) | `/roles` |
| `/help` | Show all available commands | `/help` |

## Setup

### Prerequisites

- Python 3.8 or higher
- discord.py 2.0 or higher
- A Discord Bot Token
