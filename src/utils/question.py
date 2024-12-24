async def make_question(ctx, bot, question, timeout=300):
    """Make a question to user."""
    await ctx.message.delete()
    question = await ctx.send(question)
    answer = await bot.wait_for('message', check=lambda message: message.author == ctx.author, timeout=timeout)
    return answer


async def make_private_question(ctx, bot, question, timeout=300):
    """Make a question to user in private."""
    await ctx.message.delete()
    await ctx.author.send(question)
    answer = await bot.wait_for('message', check=lambda message: message.author == ctx.author, timeout=timeout)
    return answer
