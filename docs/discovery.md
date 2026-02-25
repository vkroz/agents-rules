Here we gather and consolidate best practices of using claude code and cursor. 

The objective is to create consoliudated list of best practices, and translate them in capabilities of `agent-pack` tool.

## Claude Code

### Facts
- Claude’s context window fills up fast, and performance degrades as it fills.


### Best Practices

- Keeping context window small is critical for performance.
    - You can add session compaction instructions to CLAUDE.md file.
    - Reduce token usage
        - CLI tools use less context than MCP servers.
        - Install code intelligence plugins for typed languages
            - https://code.claude.com/docs/en/discover-plugins#code-intelligence
        - Offload processing to hooks and skills
        - Move instructions from CLAUDE.md to skills
        - Adjust extended thinking
        - Delegate verbose operations to subagents
- Give Claude a way to verify its work
- Explore first, then plan, then code
- Provide specific context in your prompts
- Provide rich content
- Configure your environment 
    - Write an effective CLAUDE.md
        - Keep it short, review and update regularly
    - Configure permissions
    - Use CLI tools
    - Connect MCP servers
    - Setup hooks
    - Create skills
    

