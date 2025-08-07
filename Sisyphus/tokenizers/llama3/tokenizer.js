async function main() {
    let input = '';
    process.stdin.setEncoding('utf8');
    for await (const chunk of process.stdin) {
        input += chunk;
    }

    const llama3Tokenizer = await import('llama3-tokenizer-js')
    const tokens = llama3Tokenizer.default.encode(input);
    console.log(tokens.length);
}
main();