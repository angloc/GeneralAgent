# Agent
import os
import logging
from typing import Union
from GeneralAgent.memory import NormalMemory
from GeneralAgent.interpreter import Interpreter
from GeneralAgent.interpreter import KnowledgeInterpreter
from GeneralAgent.interpreter import RoleInterpreter, PythonInterpreter
from GeneralAgent.utils import cut_messages, string_token_count


def default_output_callback(token):
    if token is not None:
        print(token, end="", flush=True)
    else:
        print("\n", end="", flush=True)


def default_check(check_content=None):
    show = "Confirm | Continue (Enter, yes, y, ok) or directly input your thoughts\n"
    if check_content is not None:
        show = f"{check_content}\n\n{show}"
    response = input(show)
    if response.lower() in ["", "yes", "y", "ok"]:
        return None
    else:
        return response


class Agent:
    """
    Agent
    """

    # @memory: Memory
    # @interpreters: list, interpreters
    # @output_callback: function, output_callback(content: str) -> None
    # @python_run_result: str, python run result
    # @run_level: int, python run level, use for check stack overflow level
    # @continue_run: bool, continue run when task not finished
    # @disable_python_run: bool, disable python run
    # @hide_python_code: bool, hide python code in output
    memory = None
    interpreters = []
    output_callback = None
    python_run_result = None
    run_level = 0
    continue_run = True
    disable_python_run = False
    hide_python_code = False

    def __init__(
        self,
        role: str = None,
        functions: list = [],
        knowledge_files=[],
        rag_function=None,
        workspace: str = None,
        model=None,
        token_limit=None,
        api_key=None,
        base_url=None,
        self_call=False,
        continue_run=False,
        output_callback=default_output_callback,
        disable_python_run=False,
        hide_python_code=False,
        messages=[],
        **args,
    ):
        """
        @role: str, Agent role description, e.g. "You are a novelist", defaults to None

        @functions: list, List of functions (tools) available to Agent, defaults to []

        @knowledge_files: list, List of knowledge base files. When executing delete(), the built knowledge base (embedding) will not be deleted.

        @rag_function: function, RAG function for custom RAG functions, input parameter is chat mode messages (including most recent input), return value is string.

        @workspace: str, Agent serialization directory path. If directory doesn't exist, it will be created automatically. If workspace is not None, serialized memory and python code will be loaded from workspace. Default None means no serialization, no loading. When knowledge_files is not empty, workspace must be provided

        @model: str, Model type, such as "gpt-3.5-turbo", "gpt-4o" etc.

        @token_limit: int, Model token limit. None: gpt3.5: 16*1000, gpt4: 128*1000, others: 16*1000

        @api_key: str,  OpenAI or other LLM API KEY

        @base_url: str, OpenAI or other LLM API BASE URL

        @self_call: bool, Whether to enable self-calling (Agent can write code to self-call to complete complex tasks), defaults to False.

        @continue_run: bool, Whether to auto-continue execution. Whether Agent automatically executes when task is not complete. Defaults to True.

        @output_callback: function, Output callback function for outputting Agent's streaming output results. Default None means using default output function (skills.output==print)

        @disable_python_run  (deprecated) : bool, Whether to disable python execution, defaults to False

        @hide_python_code  (deprecated) : bool, Whether to hide python code, defaults to False

        @messages: list, List of historical conversations

        @args: Other LLM conversation parameters

            temperature: float, Sampling temperature

            frequency_penalty: float, Frequency penalty, between -2 and 2

        """
        if workspace is None and len(knowledge_files) > 0:
            raise Exception(
                "workspace must be provided when knowledge_files is not empty"
            )
        if workspace is not None and not os.path.exists(workspace):
            os.makedirs(workspace)
        self.workspace = workspace
        self.disable_python_run = disable_python_run
        self.hide_python_code = hide_python_code
        self.memory = NormalMemory(serialize_path=self._memory_path, messages=messages)
        self.role_interpreter = RoleInterpreter(role=role, self_call=self_call)
        self.python_interpreter = PythonInterpreter(
            self, serialize_path=self._python_path
        )
        self.python_interpreter.function_tools = functions
        self.model = model or os.environ.get("DEFAULT_LLM_MODEL", "gpt-4o")
        self.token_limit = token_limit or 64 * 1000
        self.api_key = api_key
        self.base_url = base_url
        # self.temperature = temperature
        # self.frequency_penalty = frequency_penalty
        self.llm_args = args
        self.continue_run = continue_run
        self.knowledge_interpreter = KnowledgeInterpreter(
            workspace, knowledge_files=knowledge_files, rag_function=rag_function
        )
        self.interpreters = [
            self.role_interpreter,
            self.python_interpreter,
            self.knowledge_interpreter,
        ]
        self.enter_index = None  # Index of self.memory.messages when entering with statement
        self.output_callback = output_callback

    def __enter__(self):
        self.enter_index = len(
            self.memory.get_messages()
        )  # Record the index of self.messages
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.clear_temporary_messages()
            self.handle_exception(exc_type, exc_val, exc_tb)
        self.clear_temporary_messages()
        return False

    @property
    def _memory_path(self):
        if self.workspace is None:
            return None
        else:
            return os.path.join(self.workspace, "memory.json")

    @property
    def _python_path(self):
        if self.workspace is None:
            return None
        else:
            return os.path.join(self.workspace, "code.bin")

    @property
    def functions(self):
        return self.python_interpreter.function_tools

    @functions.setter
    def functions(self, new_value):
        self.python_interpreter.function_tools = new_value

    @property
    def role(self):
        return self.role_interpreter.role

    @role.setter
    def role(self, new_value):
        self.role_interpreter.role = new_value

    class TemporaryManager:
        def __init__(self, agent):
            self.agent = agent

        def __enter__(self):
            self.agent.enter_index = len(self.agent.memory.get_messages())
            return self.agent

        def __exit__(self, exc_type, exc_val, exc_tb):
            if exc_type:
                self.agent.clear_temporary_messages()
                self.agent.handle_exception(exc_type, exc_val, exc_tb)
            self.agent.clear_temporary_messages()
            return False

    def temporary_context(self):
        return self.TemporaryManager(self)

    def disable_output_callback(self):
        """
        Disable output callback function
        """
        self.tmp_output_callback = self.output_callback
        self.output_callback = None

    def enable_output_callback(self):
        """
        Enable output callback function
        """
        self.output_callback = self.tmp_output_callback
        self.tmp_output_callback = None

    def disable_python(self):
        """
        Disable python execution
        """
        self.disable_python_run = True

    def enable_python(self):
        """
        Enable python execution
        """
        self.disable_python_run = False

    def run(
        self,
        command: Union[str, list],
        return_type=str,
        display=False,
        verbose=True,
        user_check=False,
        check_render=None,
    ):
        """
        Execute command and return result of return_type type

        @command: Command content, str or list. list: [{'type': 'text', 'text': 'hello world'}, {'type': 'image_url', 'image_url': 'xxxx.jpg'}]

        @return_type: type, Return type, default str. Can be any python type.

        @display: bool, Whether to show streaming output

        @verbose: bool, Whether to show detailed output

        @user_check: bool, Whether user needs to confirm command execution results, default not needed

        @check_render: function, Check render function for rendering check content shown to user: check_render(result:return_type) -> str

        """
        # Code calls agent execution, directly run_level+1
        self.run_level += 1
        if not display:
            self.disable_output_callback()
        try:
            result = self._run(command, return_type=return_type, verbose=verbose)
            return result
        except Exception as e:
            logging.exception(e)
            return str(e)
        finally:
            self.run_level -= 1
            if not display:
                self.enable_output_callback()

    def user_input(self, input: Union[str, list], verbose=True):
        """
        Agent receives user input

        :input: User input content, str type or list: [{'type': 'text', 'text': 'hello world'}, {'type': 'image_url', 'image_url': 'xxxx.jpg'}]
        """
        from GeneralAgent import skills

        result = self._run(input, verbose=verbose)
        if self.continue_run and self.run_level == 0:
            # Determine whether to continue execution
            messages = self.memory.get_messages()
            messages = cut_messages(messages, 2 * 1000)
            the_prompt = "For the current state, no user input or confirmation needed, continue executing task, please reply yes, otherwise reply no"
            messages += [{"role": "system", "content": the_prompt}]
            response = skills.llm_inference(
                messages,
                model="smart",
                stream=False,
                api_key=self.api_key,
                base_url=self.base_url,
                **self.llm_args,
            )
            if "yes" in response.lower():
                result = self.run("ok")
        return result

    def _run(self, input, return_type=str, verbose=False):
        """
        agent run: parse input -> get llm messages -> run LLM and parse output

        @input: str, user's new input, None means continue to run where it stopped

        @return_type: type, return type, default str

        @verbose: bool, verbose mode
        """

        result = ""

        def local_output(token):
            nonlocal result
            if token is not None:
                result += token
            else:
                result += "\n"
            if self.output_callback is not None:
                self.output_callback(token)

        if self.run_level != 0:
            if return_type == str:
                add_content = "Directly answer the question, no need to run python\n"
                # add_content at the front
                if isinstance(input, list):
                    input = [add_content] + input
                else:
                    input = add_content + input
            else:
                add_content = (
                    "\nYou should return python values in type "
                    + str(return_type)
                    + " by run python code(```python\n#run code\nxxx\n).\n"
                )
                # add_content at the back
                if isinstance(input, list):
                    input = input + [add_content]
                else:
                    input = input + add_content
        self._memory_add_input(input)

        try_count = 0
        while True:
            messages = self._get_llm_messages()
            output_stop = self._llm_and_parse_output(messages, local_output, verbose)
            if output_stop:
                local_output(None)
                if self.python_run_result is not None:
                    result = self.python_run_result
                    self.python_run_result = None
                if return_type == str:
                    return result
                if type(result) != return_type and try_count < 1:
                    logging.info("return type should be: return_type")
                    try_count += 1
                    self._memory_add_input("return type should be " + str(return_type))
                    result = ""
                    continue
                return result

    def _memory_add_input(self, input):
        # Add user input to memory
        self.memory.add_message("user", input)

    def _get_llm_messages(self):
        # Get memory + prompt
        messages = self.memory.get_messages()
        if self.disable_python_run:
            prompt = "\n\n".join(
                [
                    interpreter.prompt(messages)
                    for interpreter in self.interpreters
                    if interpreter.__class__ != PythonInterpreter
                ]
            )
        else:
            prompt = "\n\n".join(
                [interpreter.prompt(messages) for interpreter in self.interpreters]
            )
        # Dynamically adjust memory length
        prompt_count = string_token_count(prompt)
        left_count = int(self.token_limit * 0.9) - prompt_count
        messages = cut_messages(messages, left_count)
        # Combine messages
        messages = [{"role": "system", "content": prompt}] + messages
        return messages

    def _llm_and_parse_output(self, messages, output_callback, verbose):
        outputer = _PythonCodeFilter(output_callback, verbose)
        from GeneralAgent import skills

        try:
            result = ""
            is_stop = True
            is_break = False
            response = skills.llm_inference(
                messages,
                model=self.model,
                stream=True,
                api_key=self.api_key,
                base_url=self.base_url,
                **self.llm_args,
            )
            message_id = None
            for token in response:
                if token is None:
                    break
                result += token
                outputer.process_text(token)
                interpreter: Interpreter = None
                for interpreter in self.interpreters:
                    if (
                        self.disable_python_run
                        and interpreter.__class__ == PythonInterpreter
                    ):
                        continue
                    if interpreter.output_match(result):
                        logging.debug("interpreter: " + interpreter.__class__.__name__)
                        message_id = self.memory.add_message("assistant", result)
                        self.memory.push_stack()
                        output, is_stop = interpreter.output_parse(result)
                        if self.python_run_result is not None:
                            output = output.strip()
                            if len(output) > 50000:
                                output = output[:50000] + "..."
                        self.memory.pop_stack()
                        message_id = self.memory.append_message(
                            "assistant", "\n" + output + "\n", message_id=message_id
                        )
                        result = ""
                        # if is_stop:
                        outputer.process_text(None)
                        outputer.process_text("```output\n" + output + "\n```\n")
                        if interpreter.__class__ == PythonInterpreter:
                            outputer.exit_python_code()
                        is_break = True
                        break
                if is_break:
                    break
            if len(result) > 0:
                message_id = self.memory.add_message("assistant", result)
            outputer.flush()
            return is_stop
        except Exception as e:
            logging.exception(e)
            outputer.process_text(str(e))
            outputer.flush()
            return True

    def clear(self):
        """
        Clear: Delete memory and python serialization files. Will not delete workspace and knowledge base.
        """
        if self._memory_path is not None and os.path.exists(self._memory_path):
            os.remove(self._memory_path)
        if self._python_path is not None and os.path.exists(self._python_path):
            os.remove(self._python_path)
        self.memory = NormalMemory(serialize_path=self._memory_path)
        self.python_interpreter = PythonInterpreter(
            self, serialize_path=self._python_path
        )

    def clear_temporary_messages(self):
        """
        Clear: Temporarily generated data
        """
        assert self.enter_index is not None
        self.memory.recover(self.enter_index)
        self.enter_index = None


class _PythonCodeFilter:
    """
    Python code filter, used to hide Python code blocks
    """

    def __init__(self, output_callback, verbose):
        """
        Constructor

        @output_callback: Output callback function

        @verbose: Whether to show detailed output
        """
        self.verbose = verbose
        self.in_python_code = False
        self.buffer = ""
        self.output_callback = output_callback

    def process_text(self, text):
        """
        Process input question
        """
        if self.verbose:
            self.output_callback(text)
        else:
            if text is None:
                self.flush()
                self.output_callback(None)
            else:
                if not self.in_python_code:
                    self.buffer += text
                    self._process_buffer()

    def exit_python_code(self):
        """
        Exit python code block
        """
        self.in_python_code = False

    def _process_buffer(self):
        format = "```python\n#run code\n"
        if self.buffer.endswith(format):
            self.in_python_code = True
            self.buffer = ""  # Clear buffer because we don't print ```python
        elif "```" in self.buffer and not self.in_python_code:
            # Clear content before ```
            index = self.buffer.rfind("```")
            if index != -1:
                self.output_callback(self.buffer[:index])
                self.buffer = self.buffer[index:]
            # If buffer is too large, it means it's not a python code block, output directly
            if len(self.buffer) > len(format):
                self.flush()
        else:
            self.output_callback(self.buffer)
            self.buffer = ""

    def flush(self):
        if self.buffer:
            self.output_callback(self.buffer)
            self.buffer = ""
