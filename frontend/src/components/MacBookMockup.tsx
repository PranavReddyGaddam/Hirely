import React from 'react';

interface MacBookMockupProps {
  videoSrc: string;
  autoPlay?: boolean;
  loop?: boolean;
  muted?: boolean;
}

const MacBookMockup: React.FC<MacBookMockupProps> = ({
  videoSrc,
  autoPlay = true,
  loop = true,
  muted = true,
}) => {
  return (
    <div className="w-[608px] [perspective:2000px]">
      <div className="relative w-full h-[420px] [transform:rotateX(73deg)] [transform-style:preserve-3d] origin-bottom">
        {/* Screen */}
        <div className="absolute overflow-hidden aspect-video left-0 h-[342px] -top-[343px] bg-black border-[2px] border-[#404041] rounded-md [transform:rotateX(-70deg)] origin-bottom">
          {/* Bottom bar with MacBook Air label */}
          <div className="absolute bottom-0 w-full left-0 bg-zinc-900 h-3 flex items-center justify-center text-zinc-200 text-[6px] font-thin">
            MacBook Air
          </div>
          {/* Screen content area with video */}
          <div className="absolute inset-1 mb-4 mx-1 mt-1 rounded-[3px] overflow-hidden">
            <div className="relative w-full h-full rounded-[3px] overflow-hidden flex items-center justify-center bg-black">
              {/* Video element - object-contain to prevent stretching */}
              <video
                className="w-full h-full object-contain"
                autoPlay={autoPlay}
                loop={loop}
                muted={muted}
                playsInline
              >
                <source src={videoSrc} type="video/mp4" />
                Your browser does not support the video tag.
              </video>
            </div>
          </div>
        </div>

        {/* Base/Keyboard */}
        <div className="w-[608px] h-[420px] bg-[#6F7072] rounded-[16px] border-b border-zinc-800 flex flex-col pb-3 items-start overflow-hidden">
          <div className="absolute inset-0 mt-3 bg-[#646464] w-full h-full -z-10 rounded-[28px]"></div>
          <div className="absolute bottom-[8px] left-[241px] h-[8px] bg-zinc-700/50 w-[126px] rounded-t-full -mb-4 [transform:rotateX(210deg)]"></div>
          
          {/* Top notch/hinge area */}
          <div className="h-[6.94%] w-full relative">
            <div className="absolute top-0 left-1/2 -translate-x-1/2 h-2 w-[75%] flex items-center">
              <div className="w-[10%] bg-gradient-to-b from-black via-neutral-700 to-black h-full rounded-bl-sm"></div>
              <div className="flex-grow bg-gradient-to-b from-black via-black to-zinc-700 h-full"></div>
              <div className="w-[10%] bg-gradient-to-b from-black via-neutral-700 to-black h-full rounded-br-sm"></div>
            </div>
          </div>

          {/* Keyboard area */}
          <div className="h-[50.42%] w-full relative flex">
            {/* Left speaker grille */}
            <div 
              className="my-[6px] w-[4.07%] mx-[2px]" 
              style={{
                backgroundImage: `url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" width="4" height="4" viewBox="0 0 4 4"><circle cx="2" cy="2" r="0.8" fill="rgba(0, 0, 0, 0.2)"/></svg>')`,
                backgroundRepeat: 'repeat',
                backgroundSize: '3px 3px'
              }}
            />

            {/* Keyboard */}
            <div className="w-[91.86%] rounded-md border-neutral-600/60 border-opacity-70 border relative overflow-hidden flex flex-col p-[5px]">
              <div className="absolute left-0 top-0 w-[2px] h-full bg-gradient-to-r from-neutral-600/20 via-neutral-800/10 to-transparent"></div>
              <div className="absolute right-0 top-0 w-[2px] h-full bg-gradient-to-l from-neutral-600/20 via-neutral-800/10 to-transparent"></div>
              <div className="absolute bottom-0 left-0 w-full h-[2px] bg-gradient-to-t from-neutral-600/20 via-neutral-800/10 to-transparent"></div>
              
              {/* Function keys row */}
              <div className="h-[10.03%] mb-[.6%] flex items-center gap-x-[3px] w-full">
                {['esc', 'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12'].map((key) => (
                  <div key={key} className="bg-gradient-to-t from-black via-black to-zinc-900 shadow-[inset_0_1px_0_0_rgba(255,255,255,0.1),0_1px_2px_0_rgba(0,0,0,0.3)] h-full rounded-[4px] flex-1 flex items-center justify-center text-[8px] text-neutral-400">
                    {key}
                  </div>
                ))}
                <div className="bg-gradient-to-t from-black via-black to-zinc-900 shadow-[inset_0_1px_0_0_rgba(255,255,255,0.1),0_1px_2px_0_rgba(0,0,0,0.3)] aspect-square h-full rounded-[4px]"></div>
              </div>

              {/* Number row */}
              <div className="h-[16.62%] mb-[.6%] flex items-center space-x-[2px] w-full">
                {[['~', '`'], ['!', '1'], ['@', '2'], ['#', '3'], ['$', '4'], ['%', '5'], ['^', '6'], ['&', '7'], ['*', '8'], ['(', '9'], [')', '0'], ['_', '-'], ['+', '=']].map((keys, i) => (
                  <div key={i} className="bg-gradient-to-t from-black via-black to-zinc-900 shadow-[inset_0_1px_0_0_rgba(255,255,255,0.1),0_1px_2px_0_rgba(0,0,0,0.3)] h-full rounded-[4px] flex-1 flex flex-col items-center justify-center text-[8px] text-neutral-400">
                    <div>{keys[0]}</div>
                    <div>{keys[1]}</div>
                  </div>
                ))}
                <div className="bg-gradient-to-t from-black via-black to-zinc-900 shadow-[inset_0_1px_0_0_rgba(255,255,255,0.1),0_1px_2px_0_rgba(0,0,0,0.3)] h-full rounded-[4px] flex-[1.3] flex items-end justify-end p-1 text-[8px] text-neutral-400">
                  delete
                </div>
              </div>

              {/* QWERTY row */}
              <div className="h-[16.62%] mb-[.6%] flex items-center space-x-[2px] w-full">
                <div className="bg-gradient-to-t from-black via-black to-zinc-900 shadow-[inset_0_1px_0_0_rgba(255,255,255,0.1),0_1px_2px_0_rgba(0,0,0,0.3)] h-full rounded-[4px] flex-[1.31] flex items-end justify-start p-1 text-[8px] text-neutral-400">
                  tab
                </div>
                {['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'].map((key) => (
                  <div key={key} className="bg-gradient-to-t from-black via-black to-zinc-900 shadow-[inset_0_1px_0_0_rgba(255,255,255,0.1),0_1px_2px_0_rgba(0,0,0,0.3)] h-full rounded-[4px] flex-1 flex items-center justify-center text-[8px] text-neutral-400">
                    {key}
                  </div>
                ))}
                <div className="bg-gradient-to-t from-black via-black to-zinc-900 shadow-[inset_0_1px_0_0_rgba(255,255,255,0.1),0_1px_2px_0_rgba(0,0,0,0.3)] h-full rounded-[4px] flex-1 flex flex-col items-center justify-center text-[8px] text-neutral-400">
                  <div>{'{'}</div>
                  <div>[</div>
                </div>
                <div className="bg-gradient-to-t from-black via-black to-zinc-900 shadow-[inset_0_1px_0_0_rgba(255,255,255,0.1),0_1px_2px_0_rgba(0,0,0,0.3)] h-full rounded-[4px] flex-1 flex flex-col items-center justify-center text-[8px] text-neutral-400">
                  <div>{'}'}</div>
                  <div>]</div>
                </div>
                <div className="bg-gradient-to-t from-black via-black to-zinc-900 shadow-[inset_0_1px_0_0_rgba(255,255,255,0.1),0_1px_2px_0_rgba(0,0,0,0.3)] h-full rounded-[4px] flex-1 flex flex-col items-center justify-center text-[8px] text-neutral-400">
                  <div>|</div>
                  <div>\</div>
                </div>
              </div>

              {/* ASDF row */}
              <div className="h-[16.62%] mb-[.6%] flex items-center space-x-[2px] w-full">
                <div className="bg-gradient-to-t from-black via-black to-zinc-900 shadow-[inset_0_1px_0_0_rgba(255,255,255,0.1),0_1px_2px_0_rgba(0,0,0,0.3)] h-full rounded-[4px] flex-[1.5] flex items-end justify-start p-1 text-[8px] text-neutral-400">
                  caps lock
                </div>
                {['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'].map((key) => (
                  <div key={key} className="bg-gradient-to-t from-black via-black to-zinc-900 shadow-[inset_0_1px_0_0_rgba(255,255,255,0.1),0_1px_2px_0_rgba(0,0,0,0.3)] h-full rounded-[4px] flex-1 flex items-center justify-center text-[8px] text-neutral-400">
                    {key}
                  </div>
                ))}
                <div className="bg-gradient-to-t from-black via-black to-zinc-900 shadow-[inset_0_1px_0_0_rgba(255,255,255,0.1),0_1px_2px_0_rgba(0,0,0,0.3)] h-full rounded-[4px] flex-1 flex flex-col items-center justify-center text-[8px] text-neutral-400">
                  <div>:</div>
                  <div>;</div>
                </div>
                <div className="bg-gradient-to-t from-black via-black to-zinc-900 shadow-[inset_0_1px_0_0_rgba(255,255,255,0.1),0_1px_2px_0_rgba(0,0,0,0.3)] h-full rounded-[4px] flex-1 flex flex-col items-center justify-center text-[8px] text-neutral-400">
                  <div>"</div>
                  <div>'</div>
                </div>
                <div className="bg-gradient-to-t from-black via-black to-zinc-900 shadow-[inset_0_1px_0_0_rgba(255,255,255,0.1),0_1px_2px_0_rgba(0,0,0,0.3)] h-full rounded-[4px] flex-[1.55] flex items-end justify-end p-1 text-[8px] text-neutral-400">
                  return
                </div>
              </div>

              {/* ZXCV row */}
              <div className="h-[16.62%] mb-[.5%] flex items-center space-x-[2px] w-full">
                <div className="bg-gradient-to-t from-black via-black to-zinc-900 shadow-[inset_0_1px_0_0_rgba(255,255,255,0.1),0_1px_2px_0_rgba(0,0,0,0.3)] h-full rounded-[3px] flex-[2] flex items-end justify-start p-1 text-[8px] text-neutral-400">
                  shift
                </div>
                {['Z', 'X', 'C', 'V', 'B', 'N', 'M'].map((key) => (
                  <div key={key} className="bg-gradient-to-t from-black via-black to-zinc-900 shadow-[inset_0_1px_0_0_rgba(255,255,255,0.1),0_1px_2px_0_rgba(0,0,0,0.3)] h-full rounded-[4px] flex-1 flex items-center justify-center text-[8px] text-neutral-400">
                    {key}
                  </div>
                ))}
                <div className="bg-gradient-to-t from-black via-black to-zinc-900 shadow-[inset_0_1px_0_0_rgba(255,255,255,0.1),0_1px_2px_0_rgba(0,0,0,0.3)] h-full rounded-[4px] flex-1 flex flex-col items-center justify-center text-[8px] text-neutral-400">
                  <div>&lt;</div>
                  <div>,</div>
                </div>
                <div className="bg-gradient-to-t from-black via-black to-zinc-900 shadow-[inset_0_1px_0_0_rgba(255,255,255,0.1),0_1px_2px_0_rgba(0,0,0,0.3)] h-full rounded-[4px] flex-1 flex flex-col items-center justify-center text-[8px] text-neutral-400">
                  <div>&gt;</div>
                  <div>.</div>
                </div>
                <div className="bg-gradient-to-t from-black via-black to-zinc-900 shadow-[inset_0_1px_0_0_rgba(255,255,255,0.1),0_1px_2px_0_rgba(0,0,0,0.3)] h-full rounded-[4px] flex-1 flex flex-col items-center justify-center text-[8px] text-neutral-400">
                  <div>?</div>
                  <div>/</div>
                </div>
                <div className="bg-gradient-to-t from-black via-black to-zinc-900 shadow-[inset_0_1px_0_0_rgba(255,255,255,0.1),0_1px_2px_0_rgba(0,0,0,0.3)] h-full rounded-[3px] flex-[2] flex items-end justify-end p-1 text-[8px] text-neutral-400">
                  shift
                </div>
              </div>

              {/* Bottom row */}
              <div className="h-[16.62%] flex items-end space-x-[2px] w-full">
                <div className="bg-gradient-to-t from-black via-black to-zinc-900 shadow-[inset_0_1px_0_0_rgba(255,255,255,0.1),0_1px_2px_0_rgba(0,0,0,0.3)] h-full flex-[1.2] rounded-[3px] text-[7px] text-neutral-400 flex items-end justify-start p-1">
                  fn
                </div>
                <div className="bg-gradient-to-t from-black via-black to-zinc-900 shadow-[inset_0_1px_0_0_rgba(255,255,255,0.1),0_1px_2px_0_rgba(0,0,0,0.3)] h-full flex-[1] rounded-[3px] text-[7px] text-neutral-400 flex items-end justify-center p-1">
                  control
                </div>
                <div className="bg-gradient-to-t from-black via-black to-zinc-900 shadow-[inset_0_1px_0_0_rgba(255,255,255,0.1),0_1px_2px_0_rgba(0,0,0,0.3)] h-full flex-[1] rounded-[3px] text-[7px] text-neutral-400 flex items-end justify-center p-1">
                  option
                </div>
                <div className="bg-gradient-to-t from-black via-black to-zinc-900 shadow-[inset_0_1px_0_0_rgba(255,255,255,0.1),0_1px_2px_0_rgba(0,0,0,0.3)] h-full flex-[.8] rounded-[3px] text-[7px] text-neutral-400 flex items-end justify-center p-1">
                  command
                </div>
                <div className="bg-gradient-to-t from-black via-black to-zinc-900 shadow-[inset_0_1px_0_0_rgba(255,255,255,0.1),0_1px_2px_0_rgba(0,0,0,0.3)] h-full flex-[7] rounded-[3px]"></div>
                <div className="bg-gradient-to-t from-black via-black to-zinc-900 shadow-[inset_0_1px_0_0_rgba(255,255,255,0.1),0_1px_2px_0_rgba(0,0,0,0.3)] h-full flex-[1] rounded-[3px] text-[7px] text-neutral-400 flex items-end justify-center p-1">
                  command
                </div>
                <div className="bg-gradient-to-t from-black via-black to-zinc-900 shadow-[inset_0_1px_0_0_rgba(255,255,255,0.1),0_1px_2px_0_rgba(0,0,0,0.3)] h-full flex-[.8] rounded-[3px] text-[7px] text-neutral-400 flex items-end justify-center p-1">
                  option
                </div>
                <div className="bg-gradient-to-t from-black via-black to-zinc-900 shadow-[inset_0_1px_0_0_rgba(255,255,255,0.1),0_1px_2px_0_rgba(0,0,0,0.3)] h-full flex-[1.4] rounded-[3px]"></div>
              </div>
            </div>

            {/* Right speaker grille */}
            <div 
              className="my-[6px] w-[4.07%] mx-[2px]" 
              style={{
                backgroundImage: `url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" width="4" height="4" viewBox="0 0 4 4"><circle cx="2" cy="2" r="0.8" fill="rgba(0, 0, 0, 0.2)"/></svg>')`,
                backgroundRepeat: 'repeat',
                backgroundSize: '3px 3px'
              }}
            />
          </div>

          {/* Trackpad area */}
          <div className="h-[42.64%] w-full relative flex flex-col items-center">
            <div className="w-[40.41%] h-[91.56%] rounded-md border-neutral-600/60 border-opacity-70 border border-b-2 my-auto"></div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MacBookMockup;
