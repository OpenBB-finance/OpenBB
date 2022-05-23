```text
usage: cdf [--export {csv,json,xlsx}] [-h]
```

Explanation excerpt from: https://www.probabilitycourse.com/chapter3/3_2_1_cdf.php

The cumulative distribution function (CDF) of a random variable is another method to describe the distribution of random variables. The advantage of the CDF is that it can be defined for any kind of random variable (discrete, continuous, and mixed).

The cumulative distribution function (CDF) of random variable X is defined as:

<math xmlns="http://www.w3.org/1998/Math/MathML" display="block">
  <msub>
    <mi>F</mi>
    <mi>X</mi>
  </msub>
  <mo stretchy="false">(</mo>
  <mi>x</mi>
  <mo stretchy="false">)</mo>
  <mo>=</mo>
  <mi>P</mi>
  <mo stretchy="false">(</mo>
  <mi>X</mi>
  <mo>&#x2264;<!-- ≤ --></mo>
  <mi>x</mi>
  <mo stretchy="false">)</mo>
  <mo>,</mo>
  <mrow class="MJX-TeXAtom-ORD">
    <mtext>&#xA0;for all&#xA0;</mtext>
  </mrow>
  <mi>x</mi>
  <mo>&#x2208;<!-- ∈ --></mo>
  <mrow class="MJX-TeXAtom-ORD">
    <mi mathvariant="double-struck">R</mi>
  </mrow>
  <mo>.</mo>
</math>

Contextual Example:  I toss a coin twice. Let X be the number of observed heads. Find the CDF of X

```
optional arguments:
  --export {csv,json,xlsx}
                        Export dataframe data to csv,json,xlsx file (default: )
  -h, --help            show this help message (default: False)
```

![cdf](https://user-images.githubusercontent.com/46355364/154306055-cb3bb1ef-0e61-40c9-bf51-d095bed8dc1b.png)


