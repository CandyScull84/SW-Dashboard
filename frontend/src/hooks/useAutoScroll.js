import { useEffect, useRef } from "react";

export default function useAutoScroll(enabled, speed=0.25, interval = 50, deps = []) {
    const listRef = useRef(null);
    const timerRef = useRef(null);

   
    useEffect(() => {
        const list = listRef.current;
        
        if (!enabled || !list) {
            console.log("useAutoScroll: disabled OR no element yet");
            return;
        }
        console.log("AUTOSCROLL RUNNING on:", list.className);
        console.log("scrollHeight:", list.scrollHeight, "clientHeight:", list.clientHeight);

        //Autoscroll only when the information is longer
        if (list.scrollHeight <= list.clientHeight) {
            console.log("usAutoScroll no need to scroll");
            return;
        }
            

        let scrollPos = 0;
        let direction = 1;

        const delay = setTimeout(() => {
            timerRef.current = setInterval(() => {
                const maxScroll = list.scrollHeight - list.clientHeight;
                if (maxScroll <= 0) return;

                scrollPos += direction * speed;

                if (scrollPos >= maxScroll) {
                    direction = -1;
                    scrollPos = maxScroll;
                } else if (scrollPos <= 0) {
                    direction = 1;
                    scrollPos = 0;
                }

                list.scrollTop = scrollPos;
            }, interval);
        }, 600);
        return () => {
            clearTimeout(delay);
            if (timerRef.current) clearInterval(timerRef.current);
        };
    }, [enabled, speed, interval, ...deps]);
    
    return listRef;
}