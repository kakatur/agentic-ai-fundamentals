# Python Lists, Dictionaries, Sets, and Tuples: Work With AI Messages

Use Python collections to prepare a short conversation history, count message roles, and remove repeated source IDs. Run the example locally; it does not call an AI model.

## Choose a collection for the job

| Type | Example | Use in this lesson | Important behavior |
|---|---|---|---|
| List | `["shipping", "returns", "shipping"]` | Ordered messages and source IDs | Mutable; retains duplicates and supports positional indexing. |
| Dictionary | `{"role": "user", "content": "A17"}` | Named message fields and role counts | Mutable; keys are unique and hashable. Insertion order is preserved. |
| Set | `{"shipping", "returns"}` | Track IDs already seen | Mutable; unique, hashable elements; do not rely on iteration order. |
| Tuple | `("user", "A17")` | A fixed role/content pair | Immutable container; its elements can themselves be mutable. |

A dictionary maps keys to values; a set holds unique values. Both require hashable keys or elements. A tuple is ordered, but unlike a list you cannot replace an element in place. An immutable tuple is hashable only if its elements are hashable.

## Keep recent conversation messages

The demo stores each message as a dictionary with `role` and `content` in an ordered list. `latest_messages(messages, 3)` returns the last three in their existing order. `messages[-3:]` makes a **shallow copy of the list**: changing the new list does not change the original list, but both lists still refer to the same message dictionaries. A zero or negative limit raises `ValueError`.

`make_history` turns those dictionaries into `(role, content)` tuples. With the four sample messages, it produces:

```text
[('assistant', 'What is your order number?'), ('user', 'A17'), ('assistant', 'It shipped today.')]
```

A tuple is useful for a fixed pair; the surrounding list keeps the conversation in sequence. This example assumes every message contains both fields. Validate external data before calling it.

## Count roles with a dictionary

`count_by_role` reads each message's `role` and uses `counts.get(role, 0) + 1`. The default zero handles the first occurrence; later occurrences increment the existing count. The four demo messages produce `{'user': 2, 'assistant': 2}`.

## Remove duplicates without losing order

`sources_in_order` uses a set for membership checks and a list for the ordered result. Each new source is added to both. A repeated source is skipped. Given `['shipping', 'returns', 'shipping', 'orders']`, the result is `['shipping', 'returns', 'orders']`.

A set alone removes duplicates, but its iteration order is not a contract for the original sequence. If order matters, retain it explicitly. The example expects string IDs; unhashable elements cannot be placed in a set.

## Build a list or produce values as needed

A list comprehension stores every result in a list:

```python
message_lengths = [len(message) for message in messages]
```

A generator expression produces each result as the program asks for it:

```python
message_lengths = (len(message) for message in messages)
```

Use the list when you need to index or reuse all the results. Use the generator when you can process the values one at a time, especially for a large input, because it does not store the whole result list in memory. A generator is consumed as you iterate over it.

## Interview questions

- **Basic:** How do lists, tuples, sets, and dictionaries differ, and when would you use each? A list is an ordered, changeable sequence; a tuple is ordered but cannot be changed in place; a set stores unique hashable items; and a dictionary maps keys to values. Choose based on how you need to store and access the data.
- **Intermediate:** When would you use a generator expression instead of a list comprehension? A list comprehension builds a list immediately. A generator expression produces values as you iterate, which can use less memory for a large sequence.
- **Advanced:** Does slicing a list create independent nested objects? No. Slicing creates a new list containing references to the same elements; modifying a nested dictionary is visible through both lists.

## Run and test

Requires Python 3.9 or newer and no third-party packages.

```bash
python3 demo.py
python3 -m unittest -v
```

Try adding another message and a repeated source ID. Predict the recent history, counts, and unique sources before running the demo.

References: Python data structures [https://docs.python.org/3/tutorial/datastructures.html]; Python built-in types [https://docs.python.org/3/library/stdtypes.html]; Python Functional Programming HOWTO [https://docs.python.org/3/howto/functional.html].
