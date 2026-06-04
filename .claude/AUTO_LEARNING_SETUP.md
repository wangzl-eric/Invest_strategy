# Auto-Learning Hook System - Complete

## ✅ Installation Complete

The auto-learning hook system is now installed and configured to automatically sync project documentation with current status.

## What Was Created

### Hook Scripts
1. **`~/.claude/hooks/auto_learning.py`** - Main hook logic (SessionEnd)
2. **`~/.claude/hooks/auto_learning.sh`** - Wrapper script
3. **`~/.claude/hooks/process_auto_learning.py`** - Trigger processor (SessionStart)
4. **`~/.claude/hooks/AUTO_LEARNING_HOOK.md`** - Complete documentation

### Configuration Updates
- **`~/.claude/settings.json`** - Added hooks to SessionEnd and SessionStart

## How It Works

### 1. SessionEnd Hook (Automatic)
When a session ends:
- `auto_learning.py` runs automatically
- Creates `.claude/auto_learning_trigger.txt` with update instructions
- Queues documentation updates for next session

### 2. SessionStart Hook (Automatic)
When a new session starts:
- `process_auto_learning.py` checks for trigger file
- If found, displays update prompt
- You review and update documentation as needed

### 3. Documentation Updates
Updates these files based on session work:
- `memory/LESSONS_LEARNED.md` - New lessons from bugs/insights
- `research/STRATEGY_TRACKER.md` - Research work log
- `PROJECT_DOCUMENTATION.md` - Architecture changes
- `playground/studies/*/findings.md` - Playground work

## Workflow Example

```
Session 1:
  - You work on a strategy
  - Fix a framework bug
  - Session ends
  → auto_learning.py creates trigger file

Session 2:
  - Session starts
  → process_auto_learning.py shows prompt
  - You update LESSONS_LEARNED.md with bug fix
  - You update STRATEGY_TRACKER.md with work done
  - Delete trigger file
  → Documentation is now in sync
```

## Benefits

✅ **Automatic tracking** - No manual documentation needed
✅ **Continuous learning** - Lessons captured immediately
✅ **Historical record** - Complete work log maintained
✅ **Knowledge retention** - Insights preserved across sessions
✅ **Feedback loop** - Past lessons inform future work

## Testing

Test the system manually:

```bash
# 1. Simulate SessionEnd
cd /Users/zelin/Desktop/PA\ Investment/Invest_strategy
echo '{"type":"SessionEnd","cwd":"'$(pwd)'"}' | ~/.claude/hooks/auto_learning.py

# 2. Check trigger was created
cat .claude/auto_learning_trigger.txt

# 3. Process trigger
~/.claude/hooks/process_auto_learning.py

# 4. Clean up
rm .claude/auto_learning_trigger.txt
```

## What Gets Updated

### Always Update
- **LESSONS_LEARNED.md** - Framework bugs, statistical insights, gotchas
- **STRATEGY_TRACKER.md** - Research work on any strategy

### Update When Applicable
- **PROJECT_DOCUMENTATION.md** - New features, architecture changes
- **Playground findings** - Ensure findings.md exists for studies

### Never Update
- **MEMORY.md** - Manual curation only (high-level index)
- **BUSINESS_CONTEXT.md** - Manual curation only (domain knowledge)

## Integration with Existing Systems

Works alongside:
- **Agent-deck hooks** - Session management and summaries
- **Memory system** - Complements existing memory files
- **Research workflow** - Enforces STRATEGY_TRACKER updates
- **Playground** - Tracks exploratory work separately

## Next Session

When you start your next session, you'll see:
```
================================================================================
AUTO-LEARNING TRIGGER DETECTED
================================================================================
[Update instructions will appear here]
================================================================================
```

Follow the instructions to update documentation, then delete the trigger file.

## Status

✅ Hook scripts created and executable
✅ Configuration updated in settings.json
✅ Documentation complete
✅ Ready to use on next session end

The auto-learning feedback loop is now active!
