from datetime import datetime

def displayBets(bets, ctx):
    if not bets:
        return None
    else:
        header = "{:<15} {:<15} {:<15} {:<15} {:<16}".format("Bet ID", "Coins", "Condition", "Target", "Time")
        separator = "-" * len(header)
        table_lines = [header, separator]

        for bet in bets:
            id, coins, condition, target, time = bet
            member = ctx.guild.get_member(int(target))
            target_name = member.display_name if member else str(target)

            formatted_time = datetime.fromisoformat(time).strftime("%d.%m.%Y %H:%M")

            line = "{:<15} {:<15} {:<15} {:<15} {:<16}".format(
                str(id), str(coins), str(condition), target_name, formatted_time
            )
            table_lines.append(line)

        table_content = "\n".join(table_lines)
        return table_content
