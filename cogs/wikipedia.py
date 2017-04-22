from discord.ext import commands
import aiohttp

class Wikipedia:
	"""
	Le Wikipedia Cog
	"""
	def __init__(self, bot):
		self.bot = bot

	@commands.command(pass_context=True, name='wikipedia', aliases=['wiki', 'w'])
	async def _wikipedia(self, context, *query: str):
		"""
		Get information from Wikipedia
		"""
		try:
			url = 'https://en.wikipedia.org/w/api.php?'
			payload = {}
			payload['action'] = 'query'
			payload['format'] = 'json'
			payload['prop'] = 'extracts'
			payload['titles'] = " ".join(query).replace(' ', '_')
			payload['exsentences'] = '3'
			payload['redirects'] = '1'
			payload['explaintext'] = '1'
			headers = {'user-agent': 'Red-cog/1.0'}
			conn = aiohttp.TCPConnector(verify_ssl=False)
			session = aiohttp.ClientSession(connector=conn)
			async with session.get(url, params=payload, headers=headers) as r:
				result = await r.json()
			session.close()
			if '-1' not in result['query']['pages']:
				for page in result['query']['pages']:
					title = result['query']['pages'][page]['title']
					description = result['query']['pages'][page]['extract']
				message = '\n{}\n\n{}'.format(title, description)
			else:
				message = 'I\'m sorry, I can\'t find {}'.format(" ".join(query))
		except Exception as e:
			message = 'Something went terribly wrong! [{}]'.format(e)
		await self.bot.say('```{}```'.format(message))



def setup(bot):
	n = Wikipedia(bot)
	bot.add_cog(n)
