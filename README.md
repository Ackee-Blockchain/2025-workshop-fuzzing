# Art of Manually guided fuzzing

## Usage of Wake for Testing

### Installation of wake

```bash
pip install eth-wake
```

###

### Initialize wake project

```bash
wake up
```

Desceibe each directory and especially config file.

### VSCode Exstension

How to see detector result

### Usage of detector and printer from wake

Detector or printer result stored in `.wake/`

## Testing with Wake

```bash
wake test tests/test_default.py
```

### Usefull functions during test

#### Call trace

```python
print(tx.call_trace)
```

#### Events

```python
print(tx.events)
```

#### Console log

```sol
import "wake/console.sol";
```

```bash
wake init pytypes
```

```python
print(tx.call_trace)
print(tx.console_log)
```

## Unit test with Wake

Show how wake is flexble to apply idea to the code and make it run attack scinario

and creating proof of concepts.

### Transaction

### Event check

event check with those arguments.

### Chains

Cross chain test

## Fuzz test with wake

Fuzzing in wake

### Manully guided Fuzzing work flow

What is manually guided fuzzing

#### MGF tips

How to write code and testing tips

#### usage of Seed

```bash
wake test tests/test_fuzz.py -S 0abcdefg...
```

#### Multi process testing

```bash
wake test tests/test_fuzz.py -P 4
```

#### Debugging mode

```bash
wake test tests/test_fuzz.py -d
```

#### Breakpoint

```python
breakpoint()
```

#### Crash log

Crash log exist at `.wake/`

#### Shrinking

Running shrinking. And it will show

```bash
wake test tests/test_fuzz.py -SH
```

Run shrank test.

```bash
wake test tests/test_fuzz.py -SR
```

### Fuzzing with example 1

- prime number decide function or square root function to describe differential testing.

### Fuzzing with example 2

- Real testing example
