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
            <div className="flex flex-row items-center justify-center">
                <p className="mr-2">{videoLegend}</p>
                <div style={{transform: 'scale(0.7)'}}>
                    <Toggle
                        isOn={isOn}
                        handleChange={() => {
                            const x = document.getElementById(youtubeLink);
                            if (x.style.display === 'none') {
                                x.style.display = 'block';
                                setIsOn(true);
                            } else {
                                x.style.display = 'none';
                                setIsOn(false);
                            }
                        }}
                    />
                </div>
            </div>
            <iframe
                id={youtubeLink} // this makes it so that the ID is unique and I can have to vids per page
                width="560"
                height="315"
                style={{display: 'block', margin: '0 auto'}}
                src={youtubeLink}
                title="YouTube video player"
                frameBorder="0"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                allowFullScreen>
            </iframe>
        </div>
    );
}
