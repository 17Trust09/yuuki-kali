import discord
from discord.ext import commands
import openai
import json
from setting import OPENAI_API_KEY, BOT_OWNER_ID
from database import add_authorized_user, remove_authorized_user, is_user_authorized, save_conversation, get_conversation

openai.api_key = OPENAI_API_KEY

def is_owner(ctx):
    return ctx.author.id == BOT_OWNER_ID

class ChatBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_users = set()

    @commands.command(name='authorize')
    @commands.check(is_owner)
    async def authorize(self, ctx, user: discord.User):
        add_authorized_user(user.id)
        await ctx.send(f'{user.name} wurde autorisiert, Befehle zu verwenden.')

    @commands.command(name='unauthorize')
    @commands.check(is_owner)
    async def unauthorize(self, ctx, user: discord.User):
        remove_authorized_user(user.id)
        await ctx.send(f'{user.name} wurde die Autorisierung entzogen.')

    @commands.command(name='yuuki')
    async def gpt(self, ctx, *, prompt: str):
        if not is_user_authorized(ctx.author.id):
            await ctx.send('Du bist nicht autorisiert, diesen Befehl zu verwenden.')
            return

        if ctx.author.id in self.active_users:
            await ctx.send('Du hast bereits eine Anfrage laufen. Bitte warte, bis diese abgeschlossen ist.')
            return

        self.active_users.add(ctx.author.id)
        thinking_message = await ctx.send(f'{ctx.author.mention} Yuuki denkt nach...')

        # Konversationsverlauf aktualisieren
        conversation = get_conversation(ctx.author.id)
        conversation.append({"role": "user", "content": prompt})

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",  # Verwenden Sie das GPT-4 Modell
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."}
                ] + conversation,
                max_tokens=150  # Sie können diese Anzahl nach Bedarf anpassen
            )

            # Antwort zum Konversationsverlauf hinzufügen
            answer = response.choices[0].message['content'].strip()
            conversation.append({"role": "assistant", "content": answer})

            save_conversation(ctx.author.id, conversation)

            await thinking_message.delete()
            await ctx.send(f'{ctx.author.mention} {answer}')
        except Exception as e:
            await thinking_message.delete()
            await ctx.send(f'Es gab einen Fehler bei der Anfrage an OpenAI: {str(e)}')
        finally:
            self.active_users.remove(ctx.author.id)

    @commands.command(name='yuuki-bild')
    async def image(self, ctx, *, prompt: str):
        if not is_user_authorized(ctx.author.id):
            await ctx.send('Du bist nicht autorisiert, diesen Befehl zu verwenden.')
            return

        if ctx.author.id in self.active_users:
            await ctx.send('Du hast bereits eine Anfrage laufen. Bitte warte, bis diese abgeschlossen ist.')
            return

        self.active_users.add(ctx.author.id)
        thinking_message = await ctx.send(f'{ctx.author.mention} Yuuki denkt nach...')

        try:
            response = openai.Image.create(
                prompt=prompt,
                n=1,
                size="1024x1024",
                model="dall-e-3"  # Verwenden Sie das DALL-E 3 Modell
            )
            image_url = response['data'][0]['url']
            await thinking_message.delete()
            await ctx.send(f'{ctx.author.mention} {image_url}')
        except Exception as e:
            await thinking_message.delete()
            await ctx.send(f'Es gab einen Fehler bei der Anfrage an OpenAI: {str(e)}')
        finally:
            self.active_users.remove(ctx.author.id)

async def setup(bot):
    await bot.add_cog(ChatBot(bot))
