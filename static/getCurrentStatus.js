  async function* fetchStatus(statusUrl) {
    const utf8Decoder = new TextDecoder('utf-8');
    // console.log(statusUrl)
    const response = await fetch(statusUrl);
    const reader = response.body.getReader();
    let { value: chunk, done: readerDone } = await reader.read();
    chunk = chunk ? utf8Decoder.decode(chunk) : '';
    console.log(chunk)

    const re = /\n|\r|\r\n/gm;

    let startIndex = 0;
    let result;

    while (true) {
      let result = re.exec(chunk);
      if (!result) {
        if (readerDone) break;
        let remainder = chunk.substr(startIndex);
        ({ value: chunk, done: readerDone } = await reader.read());
        chunk = remainder + (chunk ? utf8Decoder.decode(chunk) : '');
        startIndex = re.lastIndex = 0;
        continue;
      }
      yield chunk.substring(startIndex, result.index);
      startIndex = re.lastIndex;
    }

    if (startIndex < chunk.length) {
      // Last line didn't end in a newline char
      yield chunk.substr(startIndex);
    }
  }

  async function getCurrentStatus() {
    // console.log("fetch status: ", window.location.protocol + "//" + window.location.host  + "/getStatus")
    for await (const status of fetchStatus("./getStatus")) {
      console.log(status)
      if (status === "Finished") {
        // alert("Calculation done")
        window.location = window.location.protocol + "//" + window.location.host  + "/result"
      } else {
        const elem = document.getElementById('status');
        elem.textContent = "Status: " + status
        setTimeout(() => { getCurrentStatus(); }, 20000);
      }
    }
  }
  window.onload = function () {
    console.log("page loaded")
    getCurrentStatus()
  }