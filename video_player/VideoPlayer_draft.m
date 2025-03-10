function VideoPlayer_draft
    % Create figure
    fig = uifigure('Name', 'Video Player', 'Position', [100 100 1280 480]);

    % Create axes for displaying videos
    ax1 = uiaxes(fig, 'Position', [10 50 620 420]);
    ax2 = uiaxes(fig, 'Position', [650 50 620 420]);

    % Create button to select video files
    uibutton(fig, 'Text', 'Select Videos', 'Position', [10 10 100 30], 'ButtonPushedFcn', @selectVideos);

    % Callback function for the 'Select Videos' button
    function selectVideos(~, ~)
        % Open a file dialog to select the first video file
        %[filename1, pathname1] = uigetfile({'D:\*.mp4'}, 'Select First Video File');

        % Check if a file was selected
        % if isequal(filename1,0) || isequal(pathname1,0)
            %return; % User canceled
        %end

        % Open a file dialog to select the second video file
        %[filename2, pathname2] = uigetfile({'D:\*.mp4'}, 'Select Second Video File');

        % Check if a file was selected
        %if isequal(filename2,0) || isequal(pathname2,0)
            %return; % User canceled
        %end

        % Create VideoReader objects for both videos
        pathname1 = "D:\vids";
        pathname2 = "D:\vids";
        filename1 = "world.mp4";
        filename2 = "stright.mp4";


        video1 = VideoReader(fullfile(pathname1, filename1));
        video2 = VideoReader(fullfile(pathname2, filename2));

        % Store VideoReader objects in axes UserData
        ax1.UserData.video1 = video1;
        ax2.UserData.video2 = video2;
    end

    % Insert play, pause, and exit buttons
    insertButtons(fig, ax1, ax2);

end

function insertButtons(hFig, ax1, ax2)
    % Play button with text Start/Pause/Continue
    uicontrol(hFig, 'unit', 'pixel', 'style', 'pushbutton', 'string', 'Start', ...
        'position', [115 10 75 25], 'tag', 'PBButton123', 'callback', ...
        {@playCallback, ax1, ax2});

    % Exit button with text Exit
    uicontrol(hFig, 'unit', 'pixel', 'style', 'pushbutton', 'string', 'Exit', ...
        'position', [200 10 75 25], 'callback', ...
        {@exitCallback, hFig});
end

function startOffset = getStartOffset(videoPath)
    % This function extracts the start time offset for the "stright" video
    % You can implement this based on your video metadata
    startOffset = 50; % Replace this with your logic to get the start time offset
end

function playCallback(~, ~, ax1, ax2)
    % Define a global variable to store the video player status
    persistent isPlaying;
    if isempty(isPlaying)
        isPlaying = false;
    end

    % Check the current status and take action accordingly
    if isPlaying
        % Pause the video
        isPlaying = false;
    else
        % Continue playing the video
        isPlaying = true;
        % Get the VideoReader objects from the axes UserData
        video1 = ax1.UserData.video1;
        video2 = ax2.UserData.video2;

        % Determine which video is the "stright" video and get the start offset
        if contains(video1.Name, 'stright')
            strightVideo = video1;
            otherVideo = video2;
        else
            strightVideo = video2;
            otherVideo = video1;
        end

        startOffset = getStartOffset(strightVideo.Path);

        % Play the videos
        frameRate = max(video1.FrameRate, video2.FrameRate);

        % Set axes visibility to 'off' before starting the loop
        ax1.Visible = 'off';
        ax2.Visible = 'off';

        % Start playing the "stright" video from the offset
        while isPlaying && hasFrame(strightVideo)
            strightVideo.CurrentTime = startOffset;
            frame = readFrame(strightVideo);
            image(frame, 'Parent', ax1); % Display "stright" video in ax1
            ax1.Visible = 'off';

            % Start playing the other video when the "stright" video reaches the offset
            if strightVideo.CurrentTime >= startOffset
                if hasFrame(otherVideo)
                    frame = readFrame(otherVideo);
                    image(frame, 'Parent', ax2); % Display other video in ax2
                    ax2.Visible = 'off';
                end
            end

            drawnow;
            pause(1/frameRate); % Adjust as needed
        end
    end
end



function exitCallback(~, ~, hFig)
    % Close the figure to exit the GUI
    close(hFig);
end
