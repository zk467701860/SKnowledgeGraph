### 目前存在问题
SELECT * from java_all_api_entity WHERE id=29583

```原始声明的html
static <T,R> Collector<T,R,R> of(Supplier<R> supplier, BiConsumer<R,T> accumulator, BinaryOperator<R> combiner, Collector.Characteristics... characteristics)

<pre>static &lt;T,R&gt; <a href="../../../java/util/stream/Collector.html" title="interface in java.util.stream">Collector</a>&lt;T,R,R&gt; of(<a href="../../../java/util/function/Supplier.html" title="interface in java.util.function">Supplier</a>&lt;R&gt; supplier,
                                 <a href="../../../java/util/function/BiConsumer.html" title="interface in java.util.function">BiConsumer</a>&lt;R,T&gt; accumulator,
                                 <a href="../../../java/util/function/BinaryOperator.html" title="interface in java.util.function">BinaryOperator</a>&lt;R&gt; combiner,
                                 <a href="../../../java/util/stream/Collector.Characteristics.html" title="enum in java.util.stream">Collector.Characteristics</a>... characteristics)</pre>

```
生成的全称名字存在着问题，可能需要单独针对进行处理。

#### 1. 别名问题
可以先判断下划线是否存在
write_ Type Code

#### 2. 正则表达式有问题
" is local"生成的别名前面带有空格没有去掉