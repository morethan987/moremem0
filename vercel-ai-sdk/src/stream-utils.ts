async function filterStream(fullStream: ReadableStream) {
    const reader = fullStream.getReader();
    const filteredStream = new ReadableStream({
        async start(controller) {
            while (true) {
                const { done, value } = await reader.read();
                if (done) {
                    controller.close();
                    break;
                }
                try {
                    const chunk = JSON.parse(value); 
                    // 过滤掉 step-finish 和 step-start
                    if (chunk.type !== "step-finish" && chunk.type !== "step-start") {
                        controller.enqueue(value);
                    }
                } catch (error) {
                    // 对于无法解析的值，检查其类型
                    if (!(value.type === 'step-finish' || value.type === 'step-start')) {
                        controller.enqueue(value);
                    }
                }
            }
        }
    });

    return filteredStream;
}

export { filterStream };