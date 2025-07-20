async def start_scene(update, context):
  uid = str(update.effective_user.id)
  players = load_json("data/players.json")
  if not players[uid]['age_confirmed']:
      await update.message.reply_text("🔞 ابتدا باید تأیید سنی انجام دهید.")
      return
  # Sample sexy scene (clean version)
  await update.message.reply_text("🌌 شما و سارا وارد فضای خصوصی می‌شوید...")
  await update.message.reply_text("او لبخند می‌زند و آرام نزدیک می‌شود...")
  await update.message.reply_text("🔥 صحنه ادامه دارد...")