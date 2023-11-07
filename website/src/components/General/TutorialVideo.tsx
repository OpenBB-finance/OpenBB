import React, { useState } from "react";
import { Toggle } from "typescript-toggle";

export default function TutorialVideo(
    {
        youtubeLink,
        videoLegend="Tutorial video"
    } : {
        youtubeLink: string,
        videoLegend?: string
    }) {

    const [isOn, setIsOn] = useState(true);

    return (
        <div style={{textAlign: 'center'}}>
            <div className="flex flex-col sm:flex-row items-center justify-center">
                <p>{videoLegend}</p>
                <div style={{transform: 'scale(0.7)'}}>
                    <Toggle
                        isOn={isOn}
                        handleChange={() => setIsOn(!isOn)}
                    />
                </div>
            </div>
            {isOn && (
                <div style={{position: 'relative', paddingBottom: '56.25%', height: '0', overflow: 'hidden', maxWidth: '100%'}}>
                    <iframe
                        id={youtubeLink} // this makes it so that the ID is unique and I can have to vids per page
                        style={{position: 'absolute', top: '0', left: '0', width: '100%', height: '100%', display: 'block', margin: '0 auto'}}
                        src={youtubeLink}
                        title="YouTube video player"
                        frameBorder="0"
                        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                        allowFullScreen>
                    </iframe>
                </div>
            )}
        </div>
    );
}
