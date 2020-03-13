import discord
from discord.ext import commands, tasks

from . import db
from .config import Config
from .util import get_homeworks, get_token, InvalidToken, get_student_id

import logging
from datetime import datetime


class Notifier(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.token = None
        self.check_homeworks.start()

    def cog_unload(self):
        self.check_homeworks.cancel()

    @commands.command()
    async def add(self, ctx, username, alias=None):
        if self.token is None:
            self.token = await get_token(self.bot.session, Config.USERNAME, Config.PASSWORD)
        guild = await db.get(db.Guild, id=ctx.guild.id)
        student_id = await get_student_id(self.bot.session, username, self.token)
        if student_id is None:
            embed = discord.Embed(
                title='Alumno no encontrado',
                description=f'El alumno `{username}` no existe.',
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        student = db.Student(id=student_id, username=username, alias=alias)
        guild.students.append(student)
        db.session.commit()
        embed = discord.Embed(
            title='Estudiante añadido con éxito! ✅',
            description=f'El estudiante con username `{username}` ha sido agregado exitosamente a la base de datos. Pronto recibirás notificaciones de tus tareas en aulaplaneta.',
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

    @commands.command(aliases=['del'])
    async def delete(self, ctx, username):
        student = await db.get(db.Student, username=username)
        if student is None:
            embed = discord.Embed(
                title='El usuario no existe!',
                description=f'No se ha podido eliminar al usuario {username}',
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        db.session.delete(student)
        db.session.commit()
        embed = discord.Embed(
            title='Estudiante eliminado con éxito! ✅',
            description=f'El estudiante con username `{username}` ha sido eliminado exitosamente.',
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

    @commands.command(name='list')
    async def list_students(self, ctx):
        students = (await db.get(db.Guild, id=ctx.guild.id)).students
        embed = discord.Embed(
            title='Lista de estudiantes',
            description='',
            color=discord.Color.green()
        )
        if students:
            for student in students:
                if student.alias:
                    embed.description += f'{student.alias} ({student.username})\n\n'
                else:
                    embed.description += f'{student.username}\n\n'
        else:
            embed.description = 'No hay ningún estudiante actualmente'
        await ctx.send(embed=embed)

    @commands.command()
    async def prefix(self, ctx, new_prefix):
        guild = await db.get(db.Guild, id=ctx.guild.id)
        guild.prefix = new_prefix
        db.session.commit()
        embed = discord.Embed(
            title='Prefix editado con éxito! ✅',
            description=f'El prefix para este server ha sido cambiado a `{new_prefix}` exitosamente.',
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

    @tasks.loop(minutes=30)
    async def check_homeworks(self):
        if self.bot.session is None:
            return
        logging.info('starting check_homeworks()')
        if self.token is None:
            self.token = await get_token(self.bot.session, Config.USERNAME, Config.PASSWORD)
        for student in db.session.query(db.Student).all():
            logging.info('starting with an student')
            logging.info('gettings homeworks')
            try:
                homeworks = await get_homeworks(self.bot.session, student.id, self.token)
            except InvalidToken:
                self.token = await get_token(self.bot.session, Config.USERNAME, Config.PASSWORD)
                homeworks = await get_homeworks(self.bot.session, student.id, self.token)
            if homeworks:
                logging.info('Homeworks: ' + str(homeworks))
                homeworks = list(map(lambda homework: db.Homework(
                    id=homework['mtar_Id'],
                    name=homework['mtar_nombre'],
                    creation_date=datetime.strptime(homework['mtar_fecActivacionDesde'], '%Y-%m-%dT%H:%M:%S'),
                    due_date=datetime.strptime(homework['mtar_fecActivacionHasta'], '%Y-%m-%dT%H:%M:%S'),
                    subject=homework['asivcur_nombre'],
                    teacher=homework['prof_nombre']
                ), homeworks))
                for guild in student.guilds:
                    logging.info('starting with guild')
                    channel = discord.utils.get(self.bot.guilds, id=guild.id).system_channel
                    if channel is None:
                        continue
                    for homework in homeworks:
                        logging.info('starting with homework')
                        logging.info('checking if homework is in database')
                        db_homework = await db.get(db.CachedHomework, homework_id=homework.id, guild=guild, student=student)
                        logging.info('checking...')
                        if db_homework:
                            logging.info('homework was in database, skipping')
                            continue
                        logging.info('check ended')
                        embed = discord.Embed(
                            title=f'Nueva tarea: {homework.name}',
                            description=f'**Materia**: {homework.subject}\n**Profesor**: {homework.teacher}\n**Caduca**: {homework.due_date.strftime("%b %d, %Y")}',
                            color=discord.Color.blue(),
                            timestamp=homework.creation_date
                        )
                        alias = student.alias or student.username
                        embed.description = alias + ', tienes una nueva tarea en [aulaplaneta](https://alumnos.aulaplaneta.com/#/login)\n' + embed.description
                        logging.info('sending embed')
                        await channel.send(embed=embed)
                        logging.info('checking if homework in database x2')
                        db_homework = await db.get(db.Homework, id=homework.id)
                        if db_homework is None:
                            logging.info('homework was in database, not adding again')
                            db.session.add(homework)
                        logging.info('creating cachedhomework instance')
                        cached_homework = db.CachedHomework(homework_id=homework.id, guild=guild, student=student)
                        logging.info('adding cachedhomework')
                        db.session.add(cached_homework)
                        logging.info('---END---')
                    db.session.commit()


def setup(bot):
    bot.add_cog(Notifier(bot))
