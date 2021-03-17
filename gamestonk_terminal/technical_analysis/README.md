# TECHNICAL ANALYSIS

This menu aims to perform a technical analysis on a pre-loaded ticker chart, and the usage of the following commands along with an example will be exploited below.

[OVERLAP](#OVERLAP)
  * [ema](#ema)
    - exponential moving average
  * [sma](#sma)
    - simple moving average
  * [vwap](#vwap)
    - volume weighted average price

[MOMENTUM](#MOMENTUM)
  * [cci](#cci)
    - commodity channel index
  * [macd](#macd)
    - moving average convergence/divergence
  * [rsi](#rsi)
    - relative strength index
  * [stoch](#stoch)
    - stochastic oscillator

[TREND](#TREND)
  * [adx](#adx)
    - average directional movement index
  * [aroon](#aroon)
    - aroon indicator

[VOLATILITY](#VOLATILITY)
  * [bbands](#bbands)
    - bollinger bands

[VOLUME](#VOLUME)
  * [ad](#ad)
    - chaikin accumulation/distribution line values
  * [obv](#obv)
    - on balance volume

**S/O to https://github.com/twopirllc/pandas-ta** _Owing to this library, it is fairly easy to add other technical indicators. So, let me know if there's any that you would like. Personally I use mostly these ones, hence why I didn't add more._

# OVERLAP <a name="OVERLAP"></a>

## ema  <a name="ema"></a>
```
usage: ema [-l N_LENGTH] [-o N_OFFSET]
```
![ema](https://user-images.githubusercontent.com/25267873/108602300-33bac200-7399-11eb-971a-f23f7097aba3.png)


## sma  <a name="sma"></a>
```
usage: sma [-l L_LENGTH] [-o N_OFFSET]
```
![sma](https://user-images.githubusercontent.com/25267873/108602304-36b5b280-7399-11eb-86fe-d490fb32aaff.png)


## vwap  <a name="vwap"></a>
```
usage: vwap [-o N_OFFSET]
```
![vwap](https://user-images.githubusercontent.com/25267873/108602302-361d1c00-7399-11eb-87de-6026a2987ae0.png)


# MOMENTUM <a name="MOMENTUM"></a>

## cci  <a name="cci"></a>
```
usage: cci [-l N_LENGTH] [-s N_SCALAR] [-o N_OFFSET]
```
![cci](https://user-images.githubusercontent.com/25267873/108602745-96ad5880-739b-11eb-9e86-a1706c3ecb1f.png)


## macd  <a name="macd"></a>
```
usage: macd [-f N_FAST] [-s N_SLOW] [--signal N_SIGNAL] [-o N_OFFSET]
```
![macd](https://user-images.githubusercontent.com/25267873/108602739-92813b00-739b-11eb-8a4e-8fa7ed66b2b6.png)


## rsi  <a name="rsi"></a>
```
usage: rsi [-l N_LENGTH] [-s N_SCALAR] [-d N_DRIFT] [-o N_OFFSET]
```
![rsi](https://user-images.githubusercontent.com/25267873/108602743-957c2b80-739b-11eb-9d0d-6f530b3abb91.png)


## stoch  <a name="stoch"></a>
```
usage: stoch [-k N_FASTKPERIOD] [-d N_SLOWDPERIOD] [--slowkperiod N_SLOWKPERIOD] [-o N_OFFSET]
```
![stoch](https://user-images.githubusercontent.com/25267873/108602744-9614c200-739b-11eb-8e4d-2cdc9981cb67.png)


# TREND <a name="TREND"></a>

## adx  <a name="adx"></a>
```
usage: adx [-l N_LENGTH] [-s N_SCALAR] [-d N_DRIFT] [-o N_OFFSET]
```
![adx](https://user-images.githubusercontent.com/25267873/108602991-2bfd1c80-739d-11eb-973f-b836c1b839e6.png)


## aroon  <a name="aroon"></a>
```
usage: aroon [-l N_LENGTH] [-s N_SCALAR] [-o N_OFFSET]
```
![aroon](https://user-images.githubusercontent.com/25267873/108602987-2b648600-739d-11eb-9a90-154145190595.png)


# VOLATILITY <a name="VOLATILITY"></a>

## bbands  <a name="bbands"></a>
```
usage: bbands [-h] [-l N_LENGTH] [-s N_STD] [-m S_MAMODE] [-o N_OFFSET]
```
![bbands](https://user-images.githubusercontent.com/25267873/108602984-28699580-739d-11eb-9b82-2683a9840145.png)


# VOLUME <a name="VOLUME"></a>

## ad  <a name="ad"></a>
```
usage: ad [-o N_OFFSET] [--open]
```
![ad](https://user-images.githubusercontent.com/25267873/108603504-1f2df800-73a0-11eb-8d04-bcfd044601c1.png)


## obv  <a name="obv"></a>
```
usage: obv [-o N_OFFSET]
```
![obv](https://user-images.githubusercontent.com/25267873/108603503-1dfccb00-73a0-11eb-8da5-e5e5419a94ac.png)
