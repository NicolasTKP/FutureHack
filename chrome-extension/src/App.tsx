import { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [enabled, setEnabled] = useState(false);

  useEffect(() => {
    chrome.storage.local.get('veracityEnabled', (result) => {
      if (result.veracityEnabled !== undefined) {
        setEnabled(result.veracityEnabled);
      }
    });
  }, []);

  const onToggle = async () => {
    const newStatus = !enabled;
    setEnabled(newStatus);
    chrome.storage.local.set({ veracityEnabled: newStatus });

    let [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

    if (newStatus) {
      chrome.scripting.executeScript({
        target: { tabId: tab.id! },
        files: ["content.js"],
      }).then(() => {
        chrome.tabs.sendMessage(tab.id!, { action: "enable_veracity_checker" });
      });
    } else {
      chrome.tabs.sendMessage(tab.id!, { action: "disable_veracity_checker" });
    }
  };

  return (
    <>
      <h1>Lazada Veracity Checker</h1>
      <div className="card">
        {/* Toggle switch */}
        <label className="switch">
          <input type="checkbox" checked={enabled} onChange={onToggle} />
          <span className="slider round"></span>
        </label>
        <p>Toggle the trigger to enable the checker</p>
      </div>
    </>
  );
}

export default App;
