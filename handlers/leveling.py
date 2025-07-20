def check_level_up(player):
  xp = player.get("xp", 0)
  level = player.get("level", 1)
  if xp >= level * 100:
      player["level"] = level + 1
      player["xp"] = 0
      return True
  return False