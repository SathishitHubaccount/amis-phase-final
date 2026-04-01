"""
AMIS Base Agent
Common ReAct loop shared by all AMIS agents.
"""
import json
import textwrap
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, ToolMessage
from config import ANTHROPIC_API_KEY, MODEL_NAME, TEMPERATURE, MAX_TOKENS


# ── Pretty-print helpers ──

def _separator(char="─", width=80):
    return char * width


def _print_message_log(role, content, max_lines=50):
    """Print a message with role label and formatted content."""
    content_str = str(content)
    lines = content_str.split("\n")
    truncated = len(lines) > max_lines
    if truncated:
        lines = lines[:max_lines]

    print(f"\n{'='*80}")
    print(f"  [{role}]")
    print(f"{'─'*80}")
    for line in lines:
        print(f"  {line}")
    if truncated:
        print(f"  ... (truncated, {len(content_str)} chars total)")
    print(f"{'='*80}")


class BaseAgent:
    """
    Base class for all AMIS agents.
    Implements the ReAct (Reasoning + Acting) loop with tool execution.
    Subclasses only need to provide: agent_name, system_prompt, tools.
    """

    agent_name: str = "BASE AGENT"
    max_iterations: int = 10

    def __init__(self, system_prompt: str, tools: list):
        self.llm = ChatAnthropic(
            model=MODEL_NAME,
            anthropic_api_key=ANTHROPIC_API_KEY,
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
            timeout=300,
        )

        self.tools = tools
        self.tools_by_name = {tool.name: tool for tool in self.tools}
        self.llm_with_tools = self.llm.bind_tools(self.tools)

        self.message_history: list = []
        self.system_message = SystemMessage(content=system_prompt)
        self.trace: list = []  # structured step-by-step execution log

        print(f"\n{'#'*80}")
        print(f"#  {self.agent_name} INITIALIZED")
        print(f"#  Model : {MODEL_NAME}")
        print(f"#  Tools : {[t.name for t in self.tools]}")
        print(f"#  Temp  : {TEMPERATURE}  |  Max Tokens: {MAX_TOKENS}")
        print(f"{'#'*80}\n")

    def run(self, user_input: str) -> str:
        """
        Main agent loop: Receive input -> Think -> Call Tools -> Interpret -> Respond.

        This implements the ReAct (Reasoning + Acting) pattern:
        1. LLM reasons about what tools to call
        2. Tools execute and return results
        3. LLM interprets results and may call more tools
        4. Loop until LLM has enough info to respond
        """

        # ── Show the user message ──
        self.trace.append({"type": "user_input", "content": user_input})
        _print_message_log("USER  -->  LLM", user_input)

        self.message_history.append(HumanMessage(content=user_input))
        messages = [self.system_message] + self.message_history

        # Show what is being sent to the LLM
        print(f"\n{'*'*80}")
        print(f"  MESSAGES BEING SENT TO LLM  (total: {len(messages)} messages)")
        print(f"{'*'*80}")
        for idx, msg in enumerate(messages):
            role = type(msg).__name__.replace("Message", "").upper()
            preview = str(msg.content)[:150].replace("\n", " ")
            print(f"  [{idx}] {role:>10s} : {preview}{'...' if len(str(msg.content)) > 150 else ''}")
        print(f"{'*'*80}\n")

        # ── Agent Loop (ReAct pattern) ──
        iteration = 0

        while iteration < self.max_iterations:
            iteration += 1

            self.trace.append({"type": "iteration_start", "iteration": iteration, "message_count": len(messages)})
            print(f"\n{'>'*80}")
            print(f"  ITERATION {iteration} / {self.max_iterations}  --  Sending {len(messages)} messages to LLM...")
            print(f"{'>'*80}")

            response = self.llm_with_tools.invoke(messages)

            # ── Show what the LLM returned ──
            print(f"\n{'<'*80}")
            print(f"  LLM RESPONSE (iteration {iteration})")
            print(f"{'<'*80}")

            if response.content:
                text_content = response.content
                if isinstance(text_content, list):
                    for block in text_content:
                        if isinstance(block, dict) and block.get("type") == "text":
                            print(f"\n  [LLM TEXT]:")
                            for line in block["text"].split("\n")[:30]:
                                print(f"    {line}")
                        elif isinstance(block, dict) and block.get("type") == "tool_use":
                            print(f"\n  [LLM TOOL REQUEST]: {block.get('name', '?')}({json.dumps(block.get('input', {}), indent=2)[:200]})")
                        elif isinstance(block, str):
                            for line in block.split("\n")[:30]:
                                print(f"    {line}")
                else:
                    preview_lines = str(text_content).split("\n")[:30]
                    for line in preview_lines:
                        print(f"    {line}")
                    if len(str(text_content).split("\n")) > 30:
                        print(f"    ... (truncated)")

            # Capture LLM thinking text for trace
            _thinking = ""
            if response.content:
                if isinstance(response.content, list):
                    for _blk in response.content:
                        if isinstance(_blk, dict) and _blk.get("type") == "text":
                            _thinking += _blk["text"]
                else:
                    _thinking = str(response.content)
            if _thinking.strip():
                self.trace.append({"type": "llm_thinking", "iteration": iteration, "text": _thinking})

            # Check if the LLM wants to call tools
            if response.tool_calls:
                print(f"\n  ** LLM DECIDED TO CALL {len(response.tool_calls)} TOOL(S) **")
                for i, tc in enumerate(response.tool_calls):
                    print(f"     Tool {i+1}: {tc['name']}")
                    print(f"     Args  : {json.dumps(tc['args'], indent=2)}")
                    print(f"     ID    : {tc['id']}")
                print()

                for _tc in response.tool_calls:
                    self.trace.append({"type": "tool_call", "iteration": iteration, "tool": _tc["name"], "args": _tc["args"], "tool_id": _tc["id"]})

                messages.append(response)

                for tool_call in response.tool_calls:
                    tool_name = tool_call["name"]
                    tool_args = tool_call["args"]
                    tool_id = tool_call["id"]

                    print(f"\n  {'~'*76}")
                    print(f"  EXECUTING TOOL: {tool_name}")
                    print(f"  INPUT ARGS    : {json.dumps(tool_args)}")
                    print(f"  TOOL CALL ID  : {tool_id}")
                    print(f"  {'~'*76}")

                    tool = self.tools_by_name.get(tool_name)
                    if tool:
                        if hasattr(self, "_tool_overrides") and tool_name in self._tool_overrides:
                            result = self._tool_overrides[tool_name]
                            print(f"\n  *** SCENARIO OVERRIDE: '{tool_name}' returning injected test data ***")
                        else:
                            result = tool.invoke(tool_args)
                    else:
                        result = f"Error: Tool '{tool_name}' not found."

                    result_str = str(result)
                    self.trace.append({"type": "tool_result", "iteration": iteration, "tool": tool_name, "tool_id": tool_id, "result": result_str})

                    _print_message_log(
                        f"TOOL RESULT  -->  LLM  (tool: {tool_name}, id: {tool_id})",
                        result_str,
                        max_lines=40,
                    )

                    messages.append(
                        ToolMessage(content=result_str, tool_call_id=tool_id)
                    )

                print(f"\n  Messages in conversation now: {len(messages)}")
                print(f"  Looping back to LLM for next iteration...\n")

            else:
                # ── No tool calls: final answer ──
                final_response = response.content
                self.trace.append({"type": "final_answer", "iteration": iteration, "content": str(final_response)})

                print(f"\n  ** LLM DECIDED: NO MORE TOOLS NEEDED -- FINAL ANSWER **")
                _print_message_log(
                    "LLM FINAL RESPONSE  -->  USER",
                    final_response,
                    max_lines=80,
                )

                self.message_history.append(AIMessage(content=final_response))

                print(f"\n  {self.agent_name} completed in {iteration} iteration(s)")
                print(f"  Conversation memory now has {len(self.message_history)} messages\n")

                return final_response

        return f"{self.agent_name} reached maximum iterations without completing analysis."

    def set_tool_overrides(self, overrides: dict) -> None:
        """
        Inject controlled tool outputs for scenario/validation testing.

        Args:
            overrides: dict mapping tool_name → result.
                       Values may be dicts (auto-serialised to JSON) or strings.
                       When the agent calls a tool whose name is in this dict,
                       the override is returned instead of the real tool.
        """
        self._tool_overrides = {
            name: json.dumps(val, indent=2) if isinstance(val, dict) else str(val)
            for name, val in overrides.items()
        }

    def reset_memory(self):
        """Clear conversation history for a fresh start."""
        self.message_history = []
        print(f"{self.agent_name} memory cleared.")

    def get_trace_report(self, verbose: bool = False) -> str:
        """Render the data flow audit for the last .run() call."""
        from tools.tracer import DataFlowTracer
        return DataFlowTracer(self.agent_name, self.trace).render(verbose=verbose)

    def save_trace(self, filepath: str) -> None:
        """Save the verbose data flow audit to a file."""
        from tools.tracer import DataFlowTracer
        DataFlowTracer(self.agent_name, self.trace).save(filepath)
