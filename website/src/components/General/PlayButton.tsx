import React from "react"
import * as DialogPrimitive from "@radix-ui/react-dialog";
import PlayIcon from "../Icons/Play"
import CloseIcon from "../Icons/Close";

export default function PlayButton({ text, pathname }) {

    const pathvalue = pathname.split("/")[3];
    const platform = pathname.split("/")[2];
    const imgname = text.split(" ")[0].toLowerCase().replace("/", "");

    //TODO - Point this to s3 bucket - need to talk to Luqman
    const img5 = `/img/${platform}/${pathvalue}/${imgname}.png`;

    //`https://openbb-web-assets.s3.amazonaws.com/docs/${platform}/${pathvalue}/${imgname}.png`

    console.log("TEXT")
    console.log(imgname);
    console.log("pathvalue");
    console.log(pathvalue);

    return (
      <DialogPrimitive.Root>
        <DialogPrimitive.Trigger className="_link-icon">
          <PlayIcon className="w-4 h-4" />
        </DialogPrimitive.Trigger>
        <DialogPrimitive.Overlay className="_modal-overlay" />
        <DialogPrimitive.Content className="_modal max-h-[50vh] p-0">
          <img className="h-full w-full" src={img5} alt={pathvalue} />
          <DialogPrimitive.Close className="absolute top-0 right-0 p-2">
            <CloseIcon className="w-4 h-4" />
          </DialogPrimitive.Close>
        </DialogPrimitive.Content>
      </DialogPrimitive.Root>
    );
  }
