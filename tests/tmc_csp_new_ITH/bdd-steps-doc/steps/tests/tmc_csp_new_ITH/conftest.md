# Test Steps and Scenarios from tests/tmc_csp_new_ITH/conftest.py

Last updated on: 18 October 2024 17:08:04

## Steps

### Given: the telescope is in ON state

**Function:** `given_the_telescope_is_in_on_state`

**Signature:**
```python
def given_the_telescope_is_in_on_state(central_node_facade):
```

**Description:**
Ensure the telescope is in ON state.

---

### Given: the subarray {subarray_id} can be used

**Function:** `subarray_can_be_used`

**Signature:**
```python
def subarray_can_be_used(subarray_id, central_node_facade, subarray_node_facade, csp, sdp, event_tracer):
```

**Description:**
Set up the subarray (and the subscriptions) to be used in the test.

---

### Given: the subarray {subarray} is in the RESOURCING state

**Function:** `subarray_in_resourcing_state`

**Signature:**
```python
def subarray_in_resourcing_state(context_fixt, subarray_node_facade, default_commands_inputs):
```

**Description:**
Ensure the subarray is in the RESOURCING state.

---

### Given: the subarray {subarray} is in the IDLE state

**Function:** `subarray_in_idle_state`

**Signature:**
```python
def subarray_in_idle_state(context_fixt, subarray_node_facade, central_node_facade, default_commands_inputs):
```

**Description:**
Ensure the subarray is in the IDLE state.

---

### Given: the subarray {subarray} is in the CONFIGURING state

**Function:** `subarray_in_configuring_state`

**Signature:**
```python
def subarray_in_configuring_state(context_fixt, subarray_node_facade, default_commands_inputs):
```

**Description:**
Ensure the subarray is in the CONFIGURING state.

---

### Given: the subarray {subarray} is in the READY state

**Function:** `subarray_in_ready_state`

**Signature:**
```python
def subarray_in_ready_state(context_fixt, subarray_node_facade, default_commands_inputs):
```

**Description:**
Ensure the subarray is in the READY state.

---

### Given: the subarray {subarray} is in the SCANNING state

**Function:** `subarray_in_scanning_state`

**Signature:**
```python
def subarray_in_scanning_state(context_fixt, subarray_node_facade, default_commands_inputs):
```

**Description:**
Ensure the subarray is in the SCANNING state.

---

