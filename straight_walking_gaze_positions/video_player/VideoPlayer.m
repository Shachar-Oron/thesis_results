function VideoPlayer
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
        [filename1, pathname] = uigetfile({'D:\*.mp4'}, 'Select First Video File');

        % Check if a file was selected
        if isequal(filename1,0) || isequal(pathname,0)
            return; % User canceled
        end

        % Open a file dialog to select the second video file
        [filename2, pathname] = uigetfile({'D:\*.mp4'}, 'Select Second Video File');

        % Check if a file was selected
        if isequal(filename2,0) || isequal(pathname,0)
            return; % User canceled
        end

        % Create VideoReader objects for both videos
        video1 = VideoReader(fullfile(pathname, filename1));
        video2 = VideoReader(fullfile(pathname, filename2));

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

        % Play the videos
        while hasFrame(video1) && hasFrame(video2) && isPlaying
            frame1 = readFrame(video1);
            % frame2 = readFrame(video2);
            
            % Clear axes before displaying new frame
            cla(ax1);
            % cla(ax2);
            
            % Display frames in the axes
            image(frame1, 'Parent', ax1);
            % image(frame2, 'Parent', ax2);
            
            % Set axes visibility to 'on'
            ax1.Visible = 'on';
            % ax2.Visible = 'on';

            % Pause for the duration of a single frame
            pause(1 / video1.FrameRate);
        end
    end
end


function exitCallback(~, ~, hFig)
    % Close the figure to exit the GUI
    close(hFig);
end
function displayVideoGUI()
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
        [filename1, pathname] = uigetfile({'D:\*.mp4'}, 'Select First Video File');

        % Check if a file was selected
        if isequal(filename1,0) || isequal(pathname,0)
            return; % User canceled
        end

        % Open a file dialog to select the second video file
        [filename2, pathname] = uigetfile({'D:\*.mp4'}, 'Select Second Video File');

        % Check if a file was selected
        if isequal(filename2,0) || isequal(pathname,0)
            return; % User canceled
        end

        % Create VideoReader objects for both videos
        video1 = VideoReader(fullfile(pathname, filename1));
        video2 = VideoReader(fullfile(pathname, filename2));
       
        % Set the desired frame rate
        desiredFrameRate = 100;

        % Get the frame rate of the first video
        frameRate1 = video1.FrameRate;
        disp(['Frame rate of the first video: ' num2str(frameRate1) ' frames per second']);

        % Get the frame rate of the second video
        frameRate2 = video2.FrameRate;
        disp(['Frame rate of the second video: ' num2str(frameRate2) ' frames per second']);

        % Calculate the frame skip factor to achieve the desired frame rate
        frameSkipFactor1 = video1.FrameRate / desiredFrameRate;
        frameSkipFactor2 = video2.FrameRate / desiredFrameRate;
        
        % Display the frame skip factors
        disp(['Frame skip factor for video 1: ' num2str(frameSkipFactor1)]);
        disp(['Frame skip factor for video 2: ' num2str(frameSkipFactor2)]);

        

        % Display both videos side by side
        while hasFrame(video1) && hasFrame(video2)
            frame1 = readFrame(video1);
            frame2 = readFrame(video2);
            imshow(frame1, 'Parent', ax1);
            imshow(frame2, 'Parent', ax2);
            drawnow;
        end
    end
end
