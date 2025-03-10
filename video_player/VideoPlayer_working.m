function VideoPlayer_draft
    % Create figure
    fig = uifigure('Name', 'Video Player', 'Position', [100 100 1280 480]);

    % Create axes for displaying videos
    ax1 = uiaxes(fig, 'Position', [10 50 620 420]);
    ax2 = uiaxes(fig, 'Position', [650 50 620 420]);

         % Create text annotations for video headlines
    annotation(fig, 'textbox', [0.07, 0.92, 0.2, 0.1], 'String', 'Pupil Lab', 'FontSize', 12, 'FontWeight', 'bold', 'EdgeColor', 'none');
    annotation(fig, 'textbox', [0.57, 0.92, 0.2, 0.1], 'String', 'Go Pro', 'FontSize', 12, 'FontWeight', 'bold', 'EdgeColor', 'none');

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
       frameRate = max(video1.FrameRate, video2.FrameRate);

        % Set axes visibility to 'off' before starting the loop
        ax1.Visible = 'off';
        ax2.Visible = 'off';

        % Determine which video is the "stright" video and get the start offset
        if contains(video1.Name, 'stright')
            startOffset = getStartOffset(video1.Path);
            video1.CurrentTime = startOffset;
        else
            startOffset = getStartOffset(video2.Path);
            video2.CurrentTime = startOffset;
        end


        while isPlaying && (hasFrame(video1) || hasFrame(video2))
            if hasFrame(video1)
                frame1 = readFrame(video1);
                image(frame1, 'Parent', ax1);
            end

            if hasFrame(video2)
                frame2 = readFrame(video2);
                image(frame2, 'Parent', ax2);
            end

            % Batch updates and call drawnow once per iteration
            drawnow limitrate;
            pause(1/frameRate); 
        end

      end
    end
%end


function exitCallback(~, ~, hFig)
    % Close the figure to exit the GUI
    close(hFig);
end
