# Bassmaster NodeJS

Analysis and Exploitation of code injection vulnerability in the Bassmaster plugin to gain OS access

## Login Credentials

`SSH: student / studentlab`

## Starting application

```bash
cd bassmaster
nodejs examples/batch.js
```

## Bassmaster

NodeJS has evolved to provide an asynchronous event-drive JS runtime, meaning that it is capable of handling **multiple** requests without the use of thread-based networking. 

The Bassmaster plugin was developed for the NodeJS `hapi` framework, that acts as a **batch processing plugin** that combines multiple requests into a single one and passes them on for further processing. While most JS code injections are on the client-side attack surface, this particular NodeJS vulnerability directly leads to **server-side code execution**. 

## Source Code Transfer

```bash
scp -r student@192.168.186.112:~/bassmaster/ .
```

[JS Injection](Bassmaster%20NodeJS%205d322ca5b67a4254985df18ce9ad6332/JS%20Injection%200fad18fe5a464220bde27ff1b7f3b99e.md)

[Crafting Exploit](Bassmaster%20NodeJS%205d322ca5b67a4254985df18ce9ad6332/Crafting%20Exploit%206343df18298441b494283e2a15cc733e.md)

[Extra Mile](Bassmaster%20NodeJS%205d322ca5b67a4254985df18ce9ad6332/Extra%20Mile%200f19735481bf4c7a995f034feb854866.md)