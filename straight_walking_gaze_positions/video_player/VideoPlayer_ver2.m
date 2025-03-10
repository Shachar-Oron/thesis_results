% Initialize Psychtoolbox
PsychDefaultSetup(2); % Set up Psychtoolbox with default settings
Screen('Preference', 'SkipSyncTests', 1); % Skip synchronization tests for now

try
    % Open a window for displaying the videos
    screenNumber = max(Screen('Screens')); % Get the screen number of the primary monitor
    [window, windowRect] = PsychImaging('OpenWindow', screenNumber, 0); % Open a window with a black background
    [screenXpixels, screenYpixels] = Screen('WindowSize', window); % Get the size of the window

    % Define paths to the video files
    path1 = "D:\vids";
    path2 = "D:\vids";
    file1 = "world.mp4";
    file2 = "stright.mp4";

    % Construct full file paths for the videos
    fullPath1 = fullfile(path1, file1);
    fullPath2 = fullfile(path2, file2);

    % Convert paths to character arrays
    fullPath1 = char(fullPath1);
    fullPath2 = char(fullPath2);

    % Check if video files exist
    if ~isfile(fullPath1)
        error('File %s does not exist', fullPath1);
    end
    if ~isfile(fullPath2)
        error('File %s does not exist', fullPath2);
    end

    % Load the videos
    movie1 = Screen('OpenMovie', window, fullPath1); % Open the first video file
    movie2 = Screen('OpenMovie', window, fullPath2); % Open the second video file

    % Start playback of the first video
    Screen('PlayMovie', movie1, 1); % Start playback immediately (0 would start paused)

    % Start playback of the second video
    Screen('PlayMovie', movie2, 1); % Start playback immediately (0 would start paused)

    % Display the videos
    while ~KbCheck % Continue until a key is pressed
        % Draw the first video in the left half of the window
        tex1 = Screen('GetMovieImage', window, movie1); % Get the next frame of the first video
        if tex1 > 0
            Screen('DrawTexture', window, tex1, [], [0, 0, screenXpixels/2, screenYpixels]); % Draw the frame on the left half of the window
            Screen('Close', tex1); % Close the texture to free up memory
        end

        % Draw the second video in the right half of the window
        tex2 = Screen('GetMovieImage', window, movie2); % Get the next frame of the second video
        if tex2 > 0
            Screen('DrawTexture', window, tex2, [], [screenXpixels/2, 0, screenXpixels, screenYpixels]); % Draw the frame on the right half of the window
            Screen('Close', tex2); % Close the texture to free up memory
        end

        % Flip the window to display the videos
        Screen('Flip', window); % Show the updated window content on the screen
    end

    % Stop and close the videos
    Screen('PlayMovie', movie1, 0); % Stop playback of the first video
    Screen('CloseMovie', movie1); % Close the first video file
    Screen('PlayMovie', movie2, 0); % Stop playback of the second video
    Screen('CloseMovie', movie2); % Close the second video file

    % Close the window and release resources
    sca; % Shortcut for Screen('CloseAll');

catch
    % If an error occurs, close the window and rethrow the error
    sca; % Close the window
    psychrethrow(psychlasterror); % Rethrow the last error to see the error message
end
