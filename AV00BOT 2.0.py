from telegram import KeyboardButton,ReplyKeyboardMarkup,ReplyKeyboardRemove,InlineKeyboardMarkup,InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
import logging
import random


class TicTacToe:

	def __init__(self):
		self.players = []
		self.index = {'a1':'   ','b1':'   ','c1':'   ','a2':'   ','b2':'   ','c2':'   ','a3':'   ','b3':'   ','c3':'   '}
		self.available = ['a1','b1','c1','a2','b2','c2','a3','b3','c3']
		self.n = 0

	def marker(self,place,mark):
		self.index[place] = mark
		self.available.remove(place)

	def replymarkup(self):
		newReplyMarkup = InlineKeyboardMarkup(inline_keyboard = [[
			InlineKeyboardButton(text = self.index['a1'], callback_data = 'a1'),
			InlineKeyboardButton(text = self.index['b1'], callback_data = 'b1'),
			InlineKeyboardButton(text = self.index['c1'], callback_data = 'c1'),
		], [
			InlineKeyboardButton(text = self.index['a2'], callback_data = 'a2'),
			InlineKeyboardButton(text = self.index['b2'], callback_data = 'b2'),
			InlineKeyboardButton(text = self.index['c2'], callback_data = 'c2'),
		], [
			InlineKeyboardButton(text = self.index['a3'], callback_data = 'a3'),
			InlineKeyboardButton(text = self.index['b3'], callback_data = 'b3'),
			InlineKeyboardButton(text = self.index['c3'], callback_data = 'c3'),
		]])

		return newReplyMarkup


	def board(self):
		return f"{self.index['a1']}|{self.index['b1']}|{self.index['c1']}\n----------\n{self.index['a2']}|{self.index['b2']}|{self.index['c2']}\n----------\n{self.index['a3']}|{self.index['b3']}|{self.index['c3']}"


	def wincheck(self):
		return self.index['a1'] == self.index['b2'] == self.index['c3'] != '   ' or self.index['a3'] == self.index['b2'] == self.index['c1'] != '   ' or self.index['a1'] == self.index['b1'] == self.index['c1'] != '   ' or self.index['a2'] == self.index['b2'] == self.index['c2'] != '   ' or self.index['a3'] == self.index['b3'] == self.index['c3'] != '   ' or self.index['a1'] == self.index['a2'] == self.index['a3'] != '   ' or self.index['b1'] ==self.index['b2'] == self.index['b3'] != '   ' or self.index['c1'] == self.index['c2'] == self.index['c3'] != '   '



class Uno:

	def __init__(self):
		self.colours = ['RED🟥','BLUE🟦','GREEN🟩','YELLOW🟨']
		self.numbers = ['ZERO0️⃣','ONE1️⃣','TWO2️⃣','THREE3️⃣','FOUR4️⃣','FIVE5️⃣','SIX6️⃣','SEVEN7️⃣','EIGHT8️⃣','NINE9️⃣','REVERSE🔃','SKIP🚫','+2️⃣']
		self.cards = ['WILD⬛️','WILD⬛️ +4️⃣']
		for colour in self.colours:
			for number in self.numbers:
				self.cards.append(f'{colour} {number}')
		self.n = 0
		self.wts = [3,3]+[1]*52
		self.players = []
		self.playercards = {}
		self.addcards = 5
		self.topcard = None

	def startgame(self):
		for player in self.players:
			self.playercards[player]= random.choices(self.cards,k=self.addcards)
		self.addcards = 0
		self.topcard = random.choice(self.cards)

	def drawcards(self):
		if self.addcards == 0:
			self.playercards[self.players[self.n]] = self.playercards[self.players[self.n]] + random.choices(self.cards,self.wts,k= 1)
		else:
			self.playercards[self.players[self.n]] = self.playercards[self.players[self.n]] + random.choices(self.cards,self.wts,k=self.addcards)

	def reverse(self):
		self.players = self.players[::-1]
		self.n = len(self.players)-1-self.n

	def win(self):
		return (len(self.playercards[self.players[self.n]])) == 0

	def matchcards(self,card):
		if card == 'Draw Card(s)':
			return True
		elif self.topcard in ['WILD⬛️','WILD⬛️ +4️⃣']:
			return True

		elif self.addcards != 0:
			return card.split()[1] in ['+2️⃣','+4️⃣']

		elif card in ['WILD⬛️','WILD⬛️ +4️⃣']:
			return True

		elif self.topcard in self.colours:
			return self.topcard == card.split()[0]

		else:
			return card.split()[0] == self.topcard.split()[0] or card.split()[1] == self.topcard.split()[1] or card.split == 'WILD⬛️'

	def replyKeyboard(self):
		keyboard = [[KeyboardButton('Draw Card(s)')]]
		for card in self.playercards[self.players[self.n]]:
			keyboard.append([KeyboardButton(card)])
		return keyboard




class TelegramBot:
	"""docstring for TelegramBot"""
	def __init__(self, apiKey):
		self.activeGames = {}
		self.apiKey = apiKey
		self.activeuno = {}
		self.colours = ['RED🟥','BLUE🟦','GREEN🟩','YELLOW🟨']
		self.numbers = ['ZERO0️⃣','ONE1️⃣','TWO2️⃣','THREE3️⃣','FOUR4️⃣','FIVE5️⃣','SIX6️⃣','SEVEN7️⃣','EIGHT8️⃣','NINE9️⃣','REVERSE🔃','SKIP🚫','+2️⃣']
		self.cards = ['WILD⬛️','WILD⬛️ +4️⃣','Draw Card(s)','RED🟥','BLUE🟦','GREEN🟩','YELLOW🟨']
		for colour in self.colours:
			for number in self.numbers:
				self.cards.append(f'{colour} {number}')


	def run(self):
		updater = Updater(self.apiKey, use_context= True)
		updater.dispatcher.add_handler(CommandHandler("ttt",self.playCommand))
		updater.dispatcher.add_handler(CommandHandler('start',self.start))
		updater.dispatcher.add_handler(CallbackQueryHandler(self.callbackqueryhandler))
		updater.dispatcher.add_handler(CommandHandler('uno',self.playuno))
		updater.dispatcher.add_handler(MessageHandler(Filters.text(self.cards),self.unomessagehandler))
		updater.dispatcher.add_handler(CommandHandler('stop',self.stopuno))
		updater.start_polling()

	def start(self,update,context):
		self.sendMessage(context,update.message.chat.id,"Hey! I currently support a TicTacToe game\nAdd me to a group to check it out with your friends\nAdditional Functionalities will be added in the future")

	def sendMessage(self,context,chatID,message,**kwargs):
		sentMessage = context.bot.send_message(chatID,message,**kwargs)
		return sentMessage

	def playCommand(self,update,context):
		sentMessage = self.sendMessage(context,update.message.chat.id, "Press the play button to join a game of TicTacToe",reply_markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Play',callback_data = 'Play')]]))
		self.activeGames[sentMessage.message_id] = TicTacToe()

	def playuno(self,update,context):
		if type(self.activeuno.get(update.message.chat.id)) == Uno:
			self.sendMessage(context,update.message.chat.id,"Another game of UNO is already active in the chat")
			return
		else:
			self.sendMessage(context,update.message.chat.id,"A game of classic UNO has started \nPress the play button to join and Press the Start button to start game when sufficient players have joined\nNote : This requires you to have a Telegram username to work",reply_markup = InlineKeyboardMarkup(inline_keyboard = [[InlineKeyboardButton(text='Play',callback_data='playUNO')],[InlineKeyboardButton(text='Start',callback_data='startUNO')]]))
			self.activeuno[update.message.chat.id] = Uno()

	def stopuno(self,update,context):
		del self.activeuno[update.message.chat.id]
		self.sendMessage(context,update.message.chat.id,f"Uno has been stopped",reply_markup = ReplyKeyboardRemove())

	def getUserName(self,user):
		try:
			return "@" + user.username
		except:
			return user.first_name


	def unomessagehandler(self,update,context):
		query = update.message.text
		player = update.message.from_user.username
		activeGame = self.activeuno.get(update.message.chat.id)
		if player != activeGame.players[activeGame.n]:
			self.sendMessage(context,update.message.chat.id,'Not your turn to play')
			return
		elif not activeGame.matchcards(query):
			self.sendMessage(context,update.message.chat.id,"You can't play this card")
			return
		else:
			if query in activeGame.colours:
				if activeGame.topcard == 'WILD⬛️ +4️⃣':
					self.sendMessage(context,update.message.chat.id,f"Top card is {query} +4️⃣",reply_markup = ReplyKeyboardRemove())
					activeGame.topcard = f"{query} +4️⃣"

					if activeGame.win():
						self.sendMessage(context,update.message.chat.id,f"{activeGame.players[activeGame.n]} Finished the game")
						activeGame.players.remove(activeGame.players[activeGame.n])
						activeGame.n -= 1
					elif len(activeGame.playercards[activeGame.players[activeGame.n]]) == 1:
						self.sendMessage(context,update.message.chat.id,f"{activeGame.players[activeGame.n]} says UNO!")
					else:
						self.sendMessage(context,update.message.chat.id,f"{activeGame.players[activeGame.n]} has {len(activeGame.playercards[activeGame.players[activeGame.n]])} cards left")

					if len(activeGame.players) == 1:
						self.sendMessage(context,update.message.chat.id,f"{activeGame.players[0]} lost the game",reply_markup= ReplyKeyboardRemove())
						del self.activeuno[update.message.chat.id]
					else:
						activeGame.n +=1
						if activeGame.n == len(activeGame.players):
							activeGame.n = 0
						self.sendMessage(context,update.message.chat.id,f"@{activeGame.players[activeGame.n]}'s Turn",reply_markup = ReplyKeyboardMarkup(keyboard= activeGame.replyKeyboard(),resize_keyboard=True,selective=True))
				else:
					self.sendMessage(context,update.message.chat.id,f"Top card is {query}",reply_markup = ReplyKeyboardRemove())
					activeGame.topcard = f"{query}  WILD"
					if activeGame.win():
						self.sendMessage(context,update.message.chat.id,f"{activeGame.players[activeGame.n]} Finished the game")
						activeGame.players.remove(activeGame.players[activeGame.n])
						activeGame.n -= 1
					elif len(activeGame.playercards[activeGame.players[activeGame.n]]) == 1:
						self.sendMessage(context,update.message.chat.id,f"{activeGame.players[activeGame.n]} says UNO!")
					else:
						self.sendMessage(context,update.message.chat.id,f"{activeGame.players[activeGame.n]} has {len(activeGame.playercards[activeGame.players[activeGame.n]])} cards left")

					if len(activeGame.players) == 1:
						self.sendMessage(context,update.message.chat.id,f"{activeGame.players[0]} lost the game",reply_markup= ReplyKeyboardRemove())
						del self.activeuno[update.message.chat.id]
					else:
						activeGame.n +=1
						if activeGame.n == len(activeGame.players):
							activeGame.n = 0
						self.sendMessage(context,update.message.chat.id,f"@{activeGame.players[activeGame.n]}'s Turn",reply_markup = ReplyKeyboardMarkup(keyboard= activeGame.replyKeyboard(),resize_keyboard=True,selective=True))

			elif query == 'WILD⬛️ +4️⃣':
				activeGame.addcards += 4
				activeGame.topcard = query
				activeGame.playercards[activeGame.players[activeGame.n]].remove(query)
				self.sendMessage(context,update.message.chat.id,f"@{activeGame.players[activeGame.n]} played {query} \nChoose your colour",reply_markup = ReplyKeyboardMarkup(keyboard= [[KeyboardButton(text='RED🟥')],[KeyboardButton(text= 'BLUE🟦')],[KeyboardButton(text= 'GREEN🟩')],[KeyboardButton(text= 'YELLOW🟨')]],resize_keyboard= True,selective =True))

			elif query == 'WILD⬛️':
				activeGame.topcard = query
				activeGame.playercards[activeGame.players[activeGame.n]].remove(query)
				self.sendMessage(context,update.message.chat.id,f"@{activeGame.players[activeGame.n]} played {query} \nChoose your colour",reply_markup = ReplyKeyboardMarkup(keyboard= [[KeyboardButton(text='RED🟥')],[KeyboardButton(text= 'BLUE🟦')],[KeyboardButton(text= 'GREEN🟩')],[KeyboardButton(text= 'YELLOW🟨')]],resize_keyboard= True,selective =True))


			elif query.split()[1] == 'REVERSE🔃':
				activeGame.topcard = query
				activeGame.playercards[activeGame.players[activeGame.n]].remove(query)
				activeGame.reverse()
				self.sendMessage(context,update.message.chat.id,f"{activeGame.players[activeGame.n]} played {query}",reply_markup = ReplyKeyboardRemove())
				if activeGame.win():
					self.sendMessage(context,update.message.chat.id,f"{activeGame.players[activeGame.n]} Finished the game")
					activeGame.players.remove(activeGame.players[activeGame.n])
					activeGame.n -= 1
				elif len(activeGame.playercards[activeGame.players[activeGame.n]]) == 1:
					self.sendMessage(context,update.message.chat.id,f"{activeGame.players[activeGame.n]} says UNO!")
				else:
					self.sendMessage(context,update.message.chat.id,f"{activeGame.players[activeGame.n]} has {len(activeGame.playercards[activeGame.players[activeGame.n]])} cards left")

				if len(activeGame.players) == 1:
					self.sendMessage(context,update.message.chat.id,f"{activeGame.players[0]} lost the game",reply_markup= ReplyKeyboardRemove())
					del self.activeuno[update.message.chat.id]
				else:
					activeGame.n += 1
					if activeGame.n == len(activeGame.players):
						activeGame.n = 0
					self.sendMessage(context,update.message.chat.id,f"@{activeGame.players[activeGame.n]}'s Turn",reply_markup = ReplyKeyboardMarkup(keyboard= activeGame.replyKeyboard(),resize_keyboard=True,selective=True))

			elif query.split()[1] == 'SKIP🚫':
				activeGame.topcard = query
				activeGame.playercards[activeGame.players[activeGame.n]].remove(query)
				self.sendMessage(context,update.message.chat.id,f"{activeGame.players[activeGame.n]} played {query}",reply_markup = ReplyKeyboardRemove())
				if activeGame.win():
					self.sendMessage(context,update.message.chat.id,f"{activeGame.players[activeGame.n]} Finished the game")
					activeGame.players.remove(activeGame.players[activeGame.n])
					activeGame.n -= 1
				elif len(activeGame.playercards[activeGame.players[activeGame.n]]) == 1:
					self.sendMessage(context,update.message.chat.id,f"{activeGame.players[activeGame.n]} says UNO!")
				else:
					self.sendMessage(context,update.message.chat.id,f"{activeGame.players[activeGame.n]} has {len(activeGame.playercards[activeGame.players[activeGame.n]])} cards left")

				if len(activeGame.players) == 1:
					self.sendMessage(context,update.message.chat.id,f"{activeGame.players[0]} lost the game",reply_markup= ReplyKeyboardRemove())
					del self.activeuno[update.message.chat.id]
				else:
					activeGame.n +=2
					if activeGame.n == len(activeGame.players) + 1:
						activeGame.n = 1
					elif activeGame.n == len(activeGame.players):
						activeGame.n = 0
					self.sendMessage(context,update.message.chat.id,f"@{activeGame.players[activeGame.n]}'s Turn",reply_markup = ReplyKeyboardMarkup(keyboard= activeGame.replyKeyboard(),resize_keyboard=True,selective=True))

			elif query.split()[1] == '+2️⃣':
				activeGame.topcard = query
				activeGame.addcards += 2
				activeGame.playercards[activeGame.players[activeGame.n]].remove(query)
				self.sendMessage(context,update.message.chat.id,f"{activeGame.players[activeGame.n]} played {query}",reply_markup = ReplyKeyboardRemove())
				if activeGame.win():
					self.sendMessage(context,update.message.chat.id,f"{activeGame.players[activeGame.n]} Finished the game")
					activeGame.players.remove(activeGame.players[activeGame.n])
					activeGame.n -= 1
				elif len(activeGame.playercards[activeGame.players[activeGame.n]]) == 1:
					self.sendMessage(context,update.message.chat.id,f"{activeGame.players[activeGame.n]} says UNO!")
				else:
					self.sendMessage(context,update.message.chat.id,f"{activeGame.players[activeGame.n]} has {len(activeGame.playercards[activeGame.players[activeGame.n]])} cards left")


				if len(activeGame.players) == 1:
					self.sendMessage(context,update.message.chat.id,f"{activeGame.players[0]} lost the game",reply_markup= ReplyKeyboardRemove())
					del self.activeuno[update.message.chat.id]
				else:
					activeGame.n += 1
					if activeGame.n == len(activeGame.players):
						activeGame.n = 0
					self.sendMessage(context,update.message.chat.id,f"@{activeGame.players[activeGame.n]}'s Turn",reply_markup = ReplyKeyboardMarkup(keyboard= activeGame.replyKeyboard(),resize_keyboard=True,selective=True))

			elif query == "Draw Card(s)":
				self.sendMessage(context,update.message.chat.id,f"@{activeGame.players[activeGame.n]} has drawn card(s)\nTop card is {activeGame.topcard}",reply_markup = ReplyKeyboardRemove())
				activeGame.drawcards()
				activeGame.addcards = 0
				activeGame.n += 1
				if activeGame.n == len(activeGame.players):
					activeGame.n = 0
				self.sendMessage(context,update.message.chat.id,f"@{activeGame.players[activeGame.n]}'s Turn",reply_markup = ReplyKeyboardMarkup(keyboard= activeGame.replyKeyboard(),resize_keyboard=True,selective=True))

			else:
				activeGame.topcard = query
				activeGame.playercards[activeGame.players[activeGame.n]].remove(query)
				self.sendMessage(context,update.message.chat.id,f"{activeGame.players[activeGame.n]} played {query}",reply_markup = ReplyKeyboardRemove())
				if activeGame.win():
					self.sendMessage(context,update.message.chat.id,f"{activeGame.players[activeGame.n]} Finished the game")
					activeGame.players.remove(activeGame.players[activeGame.n])
					activeGame.n -= 1
				elif len(activeGame.playercards[activeGame.players[activeGame.n]]) == 1:
					self.sendMessage(context,update.message.chat.id,f"{activeGame.players[activeGame.n]} says UNO!")
				else:
					self.sendMessage(context,update.message.chat.id,f"{activeGame.players[activeGame.n]} has {len(activeGame.playercards[activeGame.players[activeGame.n]])} cards left")

				if len(activeGame.players) == 1:
					self.sendMessage(context,update.message.chat.id,f"{activeGame.players[0]} lost the game",reply_markup= ReplyKeyboardRemove())
					del self.activeuno[update.message.chat.id]
				else:
					activeGame.n += 1
					if activeGame.n == len(activeGame.players):
						activeGame.n = 0
					self.sendMessage(context,update.message.chat.id,f"@{activeGame.players[activeGame.n]}'s Turn",reply_markup = ReplyKeyboardMarkup(keyboard= activeGame.replyKeyboard(),resize_keyboard=True,selective=True))
		
	def callbackqueryhandler(self,update,context):
		query = update.callback_query.data

		activeGame = self.activeGames.get(update.callback_query.message.message_id)


		if query == "Play":
			newReplyMarkup = activeGame.replymarkup()
			playername = update.callback_query.from_user.first_name
			if len(activeGame.players) >= 2:
				update.callback_query.answer('Lobby is full')
				return
			elif len(activeGame.players) == 1:
				if playername in activeGame.players:
					update.callback_query.answer("You can't play against yourself.")
					return
				activeGame.players.append(playername)
				editedMessage = update.callback_query.message.edit_text(f'{activeGame.players[0]} vs {activeGame.players[1]} \n{activeGame.players[0]} is X \n{activeGame.players[1]} is O \n{activeGame.players[0]} plays first',reply_markup = newReplyMarkup)
			else:
				activeGame.players.append(playername)
				editedMessage = update.callback_query.message.edit_text(f'Press the play button to join a game of TicTacToe \nPlayer in lobby : {activeGame.players[0]}',reply_markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text = 'Play',callback_data = 'Play')]]))



		if query in ['a1','b1','c1','a2','b2','c2','a3','b3','c3']:
			playername = update.callback_query.from_user.first_name
			if not playername in activeGame.players:
				update.callback_query.answer("You are not in the game")
				return
			elif playername == activeGame.players[0] and activeGame.n % 2 == 1 or playername == activeGame.players[1] and activeGame.n % 2 == 0:
				update.callback_query.answer("Not your turn to play")
				return
			else:
				if query in activeGame.available:
					if activeGame.n%2 == 0:
						activeGame.marker(query,'X')
						activeGame.n += 1
						newReplyMarkup = activeGame.replymarkup()
						board = activeGame.board()
						if activeGame.wincheck():
							editedMessage = update.callback_query.message.edit_text(f'TicTacToe \n{activeGame.players[0]} vs {activeGame.players[1]} \n{activeGame.players[0]} Wins! \n{board}')
							del self.activeGames[update.callback_query.message.message_id]
						elif len(activeGame.available) == 0:
							editedMessage = update.callback_query.message.edit_text(f'TicTacToe \n{activeGame.players[0]} vs {activeGame.players[1]} \nIts a draw \n{board}')
							del self.activeGames[update.callback_query.message.message_id]
						else:
							editedMessage = update.callback_query.message.edit_text(f"{activeGame.players[0]} vs {activeGame.players[1]} \n{activeGame.players[0]} is X \n{activeGame.players[1]} is O \n{activeGame.players[1]}'s turn",reply_markup = newReplyMarkup)
					else:
						activeGame.marker(query,'O')
						activeGame.n +=1
						newReplyMarkup = activeGame.replymarkup()
						board = activeGame.board()
						if activeGame.wincheck():
							editedMessage = update.callback_query.message.edit_text(f'TicTacToe \n{activeGame.players[0]} vs {activeGame.players[1]} \n{activeGame.players[1]} Wins! \n{board}')
							del self.activeGames[update.callback_query.message.message_id]
						elif len(activeGame.available) == 0:
							editedMessage = update.callback_query.message.edit_text(f'TicTacToe \n{activeGame.players[0]} vs {activeGame.players[1]} \nIts a draw \n{board}')
							del self.activeGames[update.callback_query.message.message_id]
						else:
							editedMessage = update.callback_query.message.edit_text(f"{activeGame.players[0]} vs {activeGame.players[1]} \n{activeGame.players[0]} is X \n{activeGame.players[1]} is O \n{activeGame.players[0]}'s turn",reply_markup = newReplyMarkup)
				else:
					update.callback_query.answer("Please chose an empty box")

		if query in ['playUNO','startUNO']:
			activeGame = self.activeuno.get(update.callback_query.message.chat.id)
			if query == 'playUNO':
				if update.callback_query.from_user.username == None:
					update.callback_query.answer("Get yourself an username")
				elif update.callback_query.from_user.username in activeGame.players:
					update.callback_query.answer("You are already in the game")
				else:
					activeGame.players.append(update.callback_query.from_user.username)
					playerstr = 'Players : '
					for player in activeGame.players:
						playerstr = playerstr + '\n' + player
				update.callback_query.message.edit_text("A game of classic UNO has been initialised \nPress the play button to join and Press the Start button to start game when sufficient players have joined\nNote : This requires you to have a Telegram username to work" +"\n"+playerstr,reply_markup = InlineKeyboardMarkup(inline_keyboard = [[InlineKeyboardButton(text='Play',callback_data='playUNO')],[InlineKeyboardButton(text='Start',callback_data='startUNO')]]))
			elif query == 'startUNO':
				if len(activeGame.players) < 2:
					update.callback_query.answer("The game needs atleast two people to begin")
					return
				elif update.callback_query.from_user.username != activeGame.players[0]:
					update.callback_query.answer("You donot have the rights to start the game")
				else:
					activeGame.startgame()
					update.callback_query.message.edit_text(f"The game has begun\n5 cards have been distributed\nTop card is {activeGame.topcard}")
					self.sendMessage(context,update.callback_query.message.chat.id,f"@{activeGame.players[activeGame.n]}'s turn",reply_markup = ReplyKeyboardMarkup(keyboard= activeGame.replyKeyboard(),resize_keyboard=True,selective= True))

logging.basicConfig(level = logging.ERROR, format = "[%(name)s] [%(levelname)s] %(message)s")
telegramBotInstance = TelegramBot("API Key")
telegramBotInstance.run()
