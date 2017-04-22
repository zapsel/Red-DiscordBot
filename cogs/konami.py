class Konami:
	def __init__(self, bot):
		self.bot = bot

	async def listener(self, message):
		if message.author.id != self.bot.user.id:
			if '🔼 🔼 🔽 🔽 ◀ ▶ ◀ ▶ 🅱 🅰' in message.content.lower() or '🔼🔼🔽🔽◀▶◀▶🅱🅰' in message.content.lower() or '^^vv<><>ba' in message.content.lower():
				await self.bot.send_message(message.channel, 'https://www.youtube.com/watch?v=9EZkOzzUq1Q')

def setup(bot):
	n = Konami(bot)
	bot.add_listener(n.listener, "on_message")
	bot.add_cog(n)
