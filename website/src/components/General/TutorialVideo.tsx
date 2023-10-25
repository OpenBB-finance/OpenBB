import * as React from "react";

export default function TutorialVideo(
    {
        youtubeLink,
        videoLegend="Tutorial video"
    } : {
        youtubeLink: string,
        videoLegend?: string
    }) {
    return (
        <div style={{textAlign: 'center'}}>
            <button onClick={() => {
                const x = document.getElementById(youtubeLink);
                if (x.style.display === 'none') {
                x.style.display = 'block';
                } else {
                x.style.display = 'none';
                }
            }}>
                {videoLegend}
            </button>
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
