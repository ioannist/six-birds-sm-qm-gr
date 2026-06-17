# Step 18 FIV Source Record

Read source:

```text
/home/repos/six-birds-papers/Tsiokos_2026_Six_Birds_Foundations_IV_A_Catalog_of_Layer_Agnostic_Structural_Laws.tex
```

Read locations:

```text
F24: lines 1418-1514
F37: lines 6859-6898
```

F37 source content used:

```text
A joint access is a quotient j:H->J with maps a:J->Q_A and b:J->Q_B
such that a∘j=q_A and b∘j=q_B.
Complementarity is non-existence of an admissible joint quotient.
```

F24 source content used:

```text
O_s = {(h,h') : q(h)=q(h') and s(h) != s(h')}
RoleSplit(q,s) iff O_s is nonempty iff q_s=(q,s) is a strict refinement of q.
When RoleSplit holds, the layer-formation discipline selects exactly one
resolution family.
```

The paper names the six requested resolution families:

```text
MemoryLayer
HiddenUpstreamRole
BridgeMediatedRole
BudgetedRole
ScopedRole
CoarsenedRole
```

Source caveat:

The FIV paper states the obstruction theorem and names the mutually exclusive
discipline families. Repository search found no more granular predicate
definitions for the six case names. Step 18 therefore records the source
discipline phrases and applies them explicitly to the finite toy.

