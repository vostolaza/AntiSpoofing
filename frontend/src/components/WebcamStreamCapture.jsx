
import Webcam from "react-webcam";
import { useRef, useState, useCallback } from "react";
import Button from "@mui/material/Button";
import S3 from 'react-aws-s3';

const WebcamStreamCapture = () => {
  const webcamRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const [capturing, setCapturing] = useState(false);
  const [recordedChunks, setRecordedChunks] = useState([]);

  const handleStartCaptureClick = useCallback(() => {
    setCapturing(true);
    mediaRecorderRef.current = new MediaRecorder(webcamRef.current.stream, {
      mimeType: "video/webm"
    });
    mediaRecorderRef.current.addEventListener(
      "dataavailable",
      handleDataAvailable
    );
    mediaRecorderRef.current.start();
  }, [webcamRef, setCapturing, mediaRecorderRef]);

  const handleDataAvailable = useCallback(
    ({ data }) => {
      if (data.size > 0) {
        setRecordedChunks((prev) => prev.concat(data));
      }
    },
    [setRecordedChunks]
  );

  const handleStopCaptureClick = useCallback(() => {
    mediaRecorderRef.current.stop();
    setCapturing(false);
  }, [mediaRecorderRef, webcamRef, setCapturing]);

  const handleDownload = useCallback(() => {
    if (recordedChunks.length) {
      console.log('recordedChunks', recordedChunks)
      // const blob = new Blob(recordedChunks, {
      //   type: "video/webm"
      // });
      // const url = URL.createObjectURL(blob);
      // const a = document.createElement("a");
      // document.body.appendChild(a);
      // a.style = "display: none";
      // a.href = url;
      // a.download = "react-webcam-stream-capture.webm";
      // a.click();
      // window.URL.revokeObjectURL(url);
      // setRecordedChunks([]);
    }
  }, [recordedChunks]);

  return (
    <>
      <Webcam audio={false} ref={webcamRef} />
      {capturing ? (
        <Button variant="contained"onClick={handleStopCaptureClick}>Stop Capture</Button>
      ) : (
        <Button variant="contained" onClick={handleStartCaptureClick}>Start Capture</Button>
      )}
      {recordedChunks.length > 0 && (
        <Button onClick={handleDownload} variant="contained">Download</Button>
      )}
    </>
  );
};

export default WebcamStreamCapture;