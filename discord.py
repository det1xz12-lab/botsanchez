import discord
from discord import app_commands
from discord.ext import commands

# ==========================================
# ⚙️ НАСТРОЙКИ КАНАЛОВ И РОЛЕЙ (Вставь свои ID)
# ==========================================
APPLY_CHANNEL_ID = 1539713687407960084    # Канал заявок на вступление
REPORT_CHANNEL_ID = 1539715610684948480   # Канал отчетов на повышение
TRANSFER_CHANNEL_ID = 1539887484803092591 # Канал переводов

GUEST_ROLE_ID = 1539659128383864872       # Роль [00] GUEST
RECRUIT_ROLE_ID = 1539633481825652857 1539652840618721300     # Роль [01] RECRUIT

# ID ролей Хай-состава для пинга при переводах
HIGH_ROLES = {
    "SD": 1539716906762764329,  # ID роли ⚖️ 𝐇𝐈𝐆𝐇 𝐒𝐃
    "ED": 1539717070047154226,  # ID роли 💼 𝐇𝐈𝐆𝐇 𝐄𝐃
    "RD": 1539717064351154317,  # ID роли 🤝 𝐇𝐈𝐆𝐇 𝐑𝐃
    "IA": 1539717130801651883,  # ID роли 🛡️ 𝐇𝐈𝐆𝐇 𝐈𝐀
}

BOT_TOKEN = "MTUzOTcxMjI3MzY4ODMwNTc1NQ.GG84-v.foAobdXSk6XNDx8bt5K2cEzEOau7sMva9QXCTw"

# Инициализация
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


async def send_dm(user: discord.User | discord.Member, message: str):
    try:
        await user.send(message)
    except discord.Forbidden:
        pass


# ==========================================
# 1. 📝 ЗАЯВКА НА ВСТУПЛЕНИЕ (/apply)
# ==========================================
class ApplyModal(discord.ui.Modal, title="Заявка в семью SANCHEZ"):
    name_id = discord.ui.TextInput(label="Имя_Фамилия | Static ID", placeholder="Tony_Sanchez | 1024")
    age = discord.ui.TextInput(label="Реальный возраст", placeholder="18", max_length=2)
    online = discord.ui.TextInput(label="Онлайн в день", placeholder="4-6 часов")
    about = discord.ui.TextInput(label="Опыт в RP / Фракции", style=discord.TextStyle.paragraph)

    async def on_submit(self, interaction: discord.Interaction):
        channel = interaction.guild.get_channel(APPLY_CHANNEL_ID)
        if not channel:
            await interaction.response.send_message("❌ Канал не найден!", ephemeral=True)
            return

        embed = discord.Embed(title="📝 Новая заявка на вступление", color=discord.Color.blue())
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        embed.add_field(name="Кандидат", value=interaction.user.mention, inline=True)
        embed.add_field(name="IC Имя | ID", value=self.name_id.value, inline=True)
        embed.add_field(name="Возраст", value=self.age.value, inline=True)
        embed.add_field(name="Онлайн", value=self.online.value, inline=True)
        embed.add_field(name="Опыт", value=self.about.value, inline=False)

        view = ApplyButtons(applicant_id=interaction.user.id)
        await channel.send(embed=embed, view=view)
        await send_dm(interaction.user, "📥 **Ваша заявка на вступление в семью SANCHEZ успешно отправлена!** Ожидайте ответа от вербовщиков.")
        await interaction.response.send_message("✅ Заявка отправлена!", ephemeral=True)


class ApplyButtons(discord.ui.View):
    def __init__(self, applicant_id: int):
        super().__init__(timeout=None)
        self.applicant_id = applicant_id

    @discord.ui.button(label="Принять", style=discord.ButtonStyle.success, custom_id="accept_app")
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        member = guild.get_member(self.applicant_id)

        if member:
            guest_role = guild.get_role(GUEST_ROLE_ID)
            recruit_role = guild.get_role(RECRUIT_ROLE_ID)

            if guest_role and guest_role in member.roles:
                await member.remove_roles(guest_role)
            if recruit_role:
                await member.add_roles(recruit_role)

            await send_dm(member, "🎉 **Ваша заявка на вступление в семью SANCHEZ одобрена!** Роль выдана, ждем вас в игре.")

        for item in self.children:
            item.disabled = True
        await interaction.message.edit(content=f"✅ **Принял: {interaction.user.mention}**", view=self)
        await interaction.response.send_message("Заявка принята!", ephemeral=True)

    @discord.ui.button(label="Отклонить", style=discord.ButtonStyle.danger, custom_id="reject_app")
    async def reject(self, interaction: discord.Interaction, button: discord.ui.Button):
        member = interaction.guild.get_member(self.applicant_id)
        if member:
            await send_dm(member, "❌ **К сожалению, ваша заявка на вступление в семью SANCHEZ была отклонена.**")

        for item in self.children:
            item.disabled = True
        await interaction.message.edit(content=f"❌ **Отклонил: {interaction.user.mention}**", view=self)
        await interaction.response.send_message("Заявка отклонена.", ephemeral=True)


# ==========================================
# 2. 📈 ЗАЯВКА НА ПОВЫШЕНИЕ (/report)
# ==========================================
class ReportModal(discord.ui.Modal, title="Отчет на повышение"):
    rank_from_to = discord.ui.TextInput(label="С какого на какой ранг", placeholder="С [01] на [02]")
    proofs = discord.ui.TextInput(label="Ссылки на работу", style=discord.TextStyle.paragraph)

    async def on_submit(self, interaction: discord.Interaction):
        channel = interaction.guild.get_channel(REPORT_CHANNEL_ID)
        if not channel:
            await interaction.response.send_message("❌ Канал не найден!", ephemeral=True)
            return

        embed = discord.Embed(title="📈 Новый отчет на повышение", color=discord.Color.green())
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        embed.add_field(name="Сотрудник", value=interaction.user.mention, inline=True)
        embed.add_field(name="Прогресс", value=self.rank_from_to.value, inline=True)
        embed.add_field(name="Доказательства", value=self.proofs.value, inline=False)

        view = ReportButtons(applicant_id=interaction.user.id)
        await channel.send(embed=embed, view=view)
        await send_dm(interaction.user, "📥 **Ваш отчет на повышение отправлен на проверку руководству.**")
        await interaction.response.send_message("✅ Отчет отправлен!", ephemeral=True)


class ReportButtons(discord.ui.View):
    def __init__(self, applicant_id: int):
        super().__init__(timeout=None)
        self.applicant_id = applicant_id

    @discord.ui.button(label="Одобрить", style=discord.ButtonStyle.success, custom_id="accept_rep")
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        member = interaction.guild.get_member(self.applicant_id)
        if member:
            await send_dm(member, "🟢 **Ваш отчет на повышение был успешно одобрен!** Ожидайте выдачи ранга.")

        for item in self.children:
            item.disabled = True
        await interaction.message.edit(content=f"✅ **Одобрил: {interaction.user.mention}**", view=self)
        await interaction.response.send_message("Отчет одобрен!", ephemeral=True)

    @discord.ui.button(label="Отклонить", style=discord.ButtonStyle.danger, custom_id="reject_rep")
    async def reject(self, interaction: discord.Interaction, button: discord.ui.Button):
        member = interaction.guild.get_member(self.applicant_id)
        if member:
            await send_dm(member, "🔴 **Ваш отчет на повышение был отклонен.** Обратитесь к руководству за деталями.")

        for item in self.children:
            item.disabled = True
        await interaction.message.edit(content=f"❌ **Отклонил: {interaction.user.mention}**", view=self)
        await interaction.response.send_message("Отчет отклонен.", ephemeral=True)


# ==========================================
# 3. 🔄 ЗАЯВКА НА ПЕРЕВОД В ОТДЕЛ (/transfer)
# ==========================================
class TransferModal(discord.ui.Modal, title="Заявка на перевод в отдел"):
    current_dept = discord.ui.TextInput(
        label="Откуда перевод (SD / ED / RD / IA)",
        placeholder="Например: SD",
        max_length=5,
    )
    target_dept = discord.ui.TextInput(
        label="Куда перевод (SD / ED / RD / IA)",
        placeholder="Например: ED",
        max_length=5,
    )
    rank_info = discord.ui.TextInput(
        label="Ваш текущий ранг / Static ID",
        placeholder="[05] Junior Member | ID 1024",
    )
    reason = discord.ui.TextInput(
        label="Причина перевода",
        style=discord.TextStyle.paragraph,
        placeholder="Опишите причину перевода...",
    )

    async def on_submit(self, interaction: discord.Interaction):
        channel = interaction.guild.get_channel(TRANSFER_CHANNEL_ID)
        if not channel:
            await interaction.response.send_message("❌ Канал переводов не найден!", ephemeral=True)
            return

        from_tag = self.current_dept.value.strip().upper()
        to_tag = self.target_dept.value.strip().upper()

        from_role_id = HIGH_ROLES.get(from_tag)
        to_role_id = HIGH_ROLES.get(to_tag)

        from_ping = f"<@&{from_role_id}>" if from_role_id else f"`{from_tag}`"
        to_ping = f"<@&{to_role_id}>" if to_role_id else f"`{to_tag}`"

        ping_content = (
            f"🔔 **ВНИМАНИЕ ХАЙ-СОСТАВ!** {from_ping} ➔ {to_ping}\n"
            f"Заявка на перевод от {interaction.user.mention}!"
        )

        embed = discord.Embed(
            title="🔄 Заявка на перевод в другой отдел",
            color=discord.Color.gold(),
        )
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        embed.add_field(name="Сотрудник", value=interaction.user.mention, inline=True)
        embed.add_field(name="Ранг | Static ID", value=self.rank_info.value, inline=True)
        embed.add_field(name="Откуда перевод", value=f"**{from_tag}**", inline=True)
        embed.add_field(name="Куда перевод", value=f"**{to_tag}**", inline=True)
        embed.add_field(name="Причина перевода", value=self.reason.value, inline=False)

        view = TransferButtons(applicant_id=interaction.user.id, target_dept=to_tag)

        await channel.send(content=ping_content, embed=embed, view=view)
        await send_dm(
            interaction.user,
            f"📥 **Ваша заявка на перевод из `{from_tag}` в `{to_tag}` отправлена!** Руководство обоих отделов уведомлено.",
        )
        await interaction.response.send_message("✅ Заявка на перевод успешно отправлена!", ephemeral=True)


class TransferButtons(discord.ui.View):
    def __init__(self, applicant_id: int, target_dept: str):
        super().__init__(timeout=None)
        self.applicant_id = applicant_id
        self.target_dept = target_dept

    @discord.ui.button(label="Одобрить", style=discord.ButtonStyle.success, custom_id="accept_trf")
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        member = interaction.guild.get_member(self.applicant_id)
        if member:
            await send_dm(member, f"🟢 **Ваша заявка на перевод в отдел `{self.target_dept}` одобрена!**")

        for item in self.children:
            item.disabled = True
        await interaction.message.edit(content=f"✅ **Перевод одобрил: {interaction.user.mention}**", view=self)
        await interaction.response.send_message("Перевод одобрен!", ephemeral=True)

    @discord.ui.button(label="Отклонить", style=discord.ButtonStyle.danger, custom_id="reject_trf")
    async def reject(self, interaction: discord.Interaction, button: discord.ui.Button):
        member = interaction.guild.get_member(self.applicant_id)
        if member:
            await send_dm(member, f"🔴 **Ваша заявка на перевод в отдел `{self.target_dept}` была отклонена.**")

        for item in self.children:
            item.disabled = True
        await interaction.message.edit(content=f"❌ **Перевод отклонил: {interaction.user.mention}**", view=self)
        await interaction.response.send_message("Перевод отклонен.", ephemeral=True)


# ==========================================
# 🛠️ СЛЭШ-КОМАНДЫ
# ==========================================
@bot.tree.command(name="apply", description="Подать заявку на вступление")
async def apply(interaction: discord.Interaction):
    await interaction.response.send_modal(ApplyModal())

@bot.tree.command(name="report", description="Подать отчет на повышение")
async def report(interaction: discord.Interaction):
    await interaction.response.send_modal(ReportModal())

@bot.tree.command(name="transfer", description="Подать заявку на перевод в другой отдел")
async def transfer(interaction: discord.Interaction):
    await interaction.response.send_modal(TransferModal())


# ==========================================
# 🚀 ЗАПУСК
# ==========================================
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ Бот {bot.user.name} успешно запущен со всеми 3 системами!")

bot.run(BOT_TOKEN)
