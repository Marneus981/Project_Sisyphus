async function main() {
    const input = process.argv[2];
    const llama3Tokenizer = await import('llama3-tokenizer-js')
    console.log(llama3Tokenizer.default.encode(input).length)
}
main();