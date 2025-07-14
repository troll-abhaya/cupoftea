from tenshi import Tenshi

# Initialize with your API key
bot = Tenshi(api_keys=["AIzaSyCw2H-Jg_dhlKLs0j5_AEedl1qdrFmiL_Q"])

# Set system prompt
bot.set_system("You are a helpful assistant.")
response = bot.generate("Hello!")

# Generate a response
response = bot.generate("Hello!")
print(response)  # <- depends on how the API returns response
