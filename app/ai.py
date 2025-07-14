from tenshi import Tenshi
bot = Tenshi(api_keys=["AIzaSyCw2H-Jg_dhlKLs0j5_AEedl1qdrFmiL_Q"])
bot.set_system("You are a helpful assistant.")
 

@ai_bp.route('/ai/chat', methods=['GET'])
def ai_chat_page():
    return render_template('ai/only-fans-nepal.html')

@ai_bp.route('/ai/chat', methods=['POST'])
def ai_chat_api():
    user_message = request.json.get('message')
    ai_response = bot.generate(user_message)
    return jsonify({'response': ai_response})